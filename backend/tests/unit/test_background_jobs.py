from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.common.background_jobs import BackgroundJobService


class FakeSliceRepository:
    def __init__(self, items):
        self._items = items

    async def list_for_indexing(self, *, offset: int, limit: int):
        return self._items[offset : offset + limit]


class FakeContextUoW:
    def __init__(self, *, clients, executors, materials, works):
        self.clients = FakeSliceRepository(clients)
        self.executors = FakeSliceRepository(executors)
        self.materials = FakeSliceRepository(materials)
        self.works = FakeSliceRepository(works)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


class FakeSearchService:
    def __init__(self):
        self.prepared = []
        self.bulk_calls = []
        self.refreshed = []

    async def prepare_index(self, index: str, mappings, *, purge: bool):
        self.prepared.append((index, purge, mappings))

    async def bulk_index_documents(self, index: str, documents, *, refresh: bool):
        self.bulk_calls.append((index, documents, refresh))

    async def refresh_index(self, index: str):
        self.refreshed.append(index)


class FakeCacheService:
    def __init__(self):
        self.invalidated = []

    async def invalidate_prefix(self, prefix: str):
        self.invalidated.append(prefix)


class FakeDashboardService:
    def __init__(self):
        self.calls = []

    async def get_overview(self, *, date_from, date_to):
        self.calls.append((date_from, date_to))
        return None


def build_uow_factory(*, clients, executors, materials, works):
    def _factory():
        return FakeContextUoW(
            clients=clients,
            executors=executors,
            materials=materials,
            works=works,
        )

    return _factory


@pytest.mark.asyncio
async def test_reindex_search_documents_indexes_all_modules():
    now = datetime.now(timezone.utc)
    client = SimpleNamespace(
        id=str(uuid4()),
        name="Smile Studio",
        contact_person="Anna Petrova",
        phone="+79991234567",
        email="anna@smile.example",
        address="Ekaterinburg",
        comment="VIP",
    )
    executor = SimpleNamespace(
        id=str(uuid4()),
        full_name="Dmitry Ivanov",
        phone="+79990001122",
        email="dmitry@example.com",
        specialization="Ceramics",
        hourly_rate=Decimal("2800.00"),
        comment="Senior technician",
        is_active=True,
    )
    material = SimpleNamespace(
        id=str(uuid4()),
        name="Zircon Disc",
        category="Ceramics",
        unit="piece",
        stock=Decimal("24.000"),
        purchase_price=Decimal("5200.00"),
        average_price=Decimal("5450.00"),
        supplier="Dent Supply",
        min_stock=Decimal("5.000"),
        comment="Multi-layer zirconia",
    )
    work = SimpleNamespace(
        id=str(uuid4()),
        order_number="DL-2026-0001",
        client_id=client.id,
        client=client,
        executor_id=executor.id,
        executor=executor,
        work_type="Full crown",
        description="Upper molar restoration",
        status="in_progress",
        received_at=now,
        deadline_at=now,
        completed_at=None,
        price_for_client=Decimal("15500.00"),
        cost_price=Decimal("10900.00"),
        margin=Decimal("4600.00"),
        additional_expenses=Decimal("650.00"),
        labor_hours=Decimal("3.50"),
        amount_paid=Decimal("5000.00"),
        comment="Rush order",
        materials=[SimpleNamespace(material=SimpleNamespace(name="Zircon Disc"))],
    )
    search = FakeSearchService()
    cache = FakeCacheService()
    service = BackgroundJobService(
        uow_factory=build_uow_factory(
            clients=[client],
            executors=[executor],
            materials=[material],
            works=[work],
        ),
        search=search,
        cache=cache,
    )

    counts = await service.reindex_search_documents(batch_size=1)

    assert counts == {"clients": 1, "executors": 1, "materials": 1, "works": 1}
    work_call = next(indexed for indexed in search.bulk_calls if indexed[0] == "works")
    work_document = work_call[1][0][1]
    assert work_document["amount_paid"] == "5000.00"
    assert work_document["material_names"] == ["Zircon Disc"]
    assert "Upper molar restoration" in work_document["search_blob"]


@pytest.mark.asyncio
async def test_refresh_dashboard_cache_invalidates_and_warms_configured_windows():
    dashboard = FakeDashboardService()
    cache = FakeCacheService()
    service = BackgroundJobService(
        uow_factory=build_uow_factory(clients=[], executors=[], materials=[], works=[]),
        search=FakeSearchService(),
        cache=cache,
        dashboard_service_factory=lambda: dashboard,
    )

    windows = await service.refresh_dashboard_cache(windows=["all", "7d"])

    assert windows == ["all", "7d"]
    assert cache.invalidated == ["dashboard:"]
    assert dashboard.calls[0] == (None, None)
    assert dashboard.calls[1][0] is not None
    assert dashboard.calls[1][1] is not None
