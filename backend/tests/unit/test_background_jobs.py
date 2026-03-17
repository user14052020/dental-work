from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.common.background_jobs import BackgroundJobService
from app.core.config import settings


class FakeSliceRepository:
    def __init__(self, items):
        self._items = items

    async def list_for_indexing(self, *, offset: int, limit: int):
        return self._items[offset : offset + limit]

    async def list_operations_for_indexing(self, *, offset: int, limit: int):
        return self._items[offset : offset + limit]


class FakeContextUoW:
    def __init__(self, *, clients, doctors, executors, materials, operations, work_catalog, works):
        self.clients = FakeSliceRepository(clients)
        self.doctors = FakeSliceRepository(doctors)
        self.executors = FakeSliceRepository(executors)
        self.materials = FakeSliceRepository(materials)
        self.operations = FakeSliceRepository(operations)
        self.work_catalog = FakeSliceRepository(work_catalog)
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


def build_uow_factory(*, clients, doctors, executors, materials, operations, work_catalog, works):
    def _factory():
        return FakeContextUoW(
            clients=clients,
            doctors=doctors,
            executors=executors,
            materials=materials,
            operations=operations,
            work_catalog=work_catalog,
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
        default_price_adjustment_percent=Decimal("0.00"),
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
        payment_category=SimpleNamespace(code="ceramist_a", name="Керамист A"),
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
    operation = SimpleNamespace(
        id=str(uuid4()),
        code="CROWN_ZR",
        name="Циркониевая коронка",
        operation_group="Ортопедия",
        description="Базовая операция каталога",
        default_quantity=Decimal("1.00"),
        default_duration_hours=Decimal("2.50"),
        is_active=True,
        payment_rates=[
            SimpleNamespace(
                executor_category=SimpleNamespace(code="ceramist_a", name="Керамист A"),
                labor_rate=Decimal("3200.00"),
            )
        ],
    )
    doctor = SimpleNamespace(
        id=str(uuid4()),
        client_id=client.id,
        client=client,
        full_name="Сергей Волков",
        phone="+79997775544",
        email="doctor@smile.example",
        specialization="Ортопед",
        comment="Основной врач",
        is_active=True,
    )
    work_catalog_item = SimpleNamespace(
        id=str(uuid4()),
        code="CAT-001",
        name="Циркониевая коронка",
        category="Ортопедия",
        description="Каталожная позиция",
        base_price=Decimal("15500.00"),
        default_duration_hours=Decimal("3.00"),
        is_active=True,
        default_operations=[
            SimpleNamespace(
                operation=SimpleNamespace(
                    code=operation.code,
                    name=operation.name,
                )
            )
        ],
    )
    work = SimpleNamespace(
        id=str(uuid4()),
        order_number="DL-2026-0001",
        client_id=client.id,
        client=client,
        executor_id=executor.id,
        executor=executor,
        doctor_id=doctor.id,
        doctor=doctor,
        work_catalog_item_id=work_catalog_item.id,
        catalog_item=work_catalog_item,
        work_type="Full crown",
        description="Upper molar restoration",
        doctor_name="Dr. Smith",
        patient_name="John Doe",
        tooth_formula="16",
        tooth_selection=[{"tooth_code": "16", "state": "target", "surfaces": ["occlusal"]}],
        status="in_progress",
        received_at=now,
        deadline_at=now,
        completed_at=None,
        closed_at=None,
        base_price_for_client=Decimal("15500.00"),
        price_adjustment_percent=Decimal("0.00"),
        price_for_client=Decimal("15500.00"),
        cost_price=Decimal("10900.00"),
        margin=Decimal("4600.00"),
        additional_expenses=Decimal("650.00"),
        labor_hours=Decimal("3.50"),
        labor_cost=Decimal("4800.00"),
        amount_paid=Decimal("5000.00"),
        materials=[SimpleNamespace(material=SimpleNamespace(name="Zircon Disc"))],
        work_operations=[SimpleNamespace(operation_name="Циркониевая коронка")],
    )
    search = FakeSearchService()
    cache = FakeCacheService()
    service = BackgroundJobService(
        uow_factory=build_uow_factory(
            clients=[client],
            doctors=[doctor],
            executors=[executor],
            materials=[material],
            operations=[operation],
            work_catalog=[work_catalog_item],
            works=[work],
        ),
        search=search,
        cache=cache,
    )

    counts = await service.reindex_search_documents(batch_size=1)

    assert counts == {
        "clients": 1,
        "doctors": 1,
        "executors": 1,
        "materials": 1,
        "operations": 1,
        "work_catalog": 1,
        "works": 1,
    }
    operation_call = next(indexed for indexed in search.bulk_calls if indexed[0] == settings.elasticsearch_operations_index)
    operation_document = operation_call[1][0][1]
    assert "Керамист A" in operation_document["search_blob"]
    work_call = next(indexed for indexed in search.bulk_calls if indexed[0] == settings.elasticsearch_works_index)
    work_document = work_call[1][0][1]
    assert work_document["amount_paid"] == "5000.00"
    assert work_document["operation_names"] == ["Циркониевая коронка"]
    assert work_document["material_names"] == ["Zircon Disc"]
    assert work_document["tooth_selection_summary"] == "16 работа Oc"
    assert "Upper molar restoration" in work_document["search_blob"]
    assert work_document["work_catalog_item_code"] == "CAT-001"
    assert work_document["doctor_id"] == doctor.id


@pytest.mark.asyncio
async def test_refresh_dashboard_cache_invalidates_and_warms_configured_windows():
    dashboard = FakeDashboardService()
    cache = FakeCacheService()
    service = BackgroundJobService(
        uow_factory=build_uow_factory(
            clients=[],
            doctors=[],
            executors=[],
            materials=[],
            operations=[],
            work_catalog=[],
            works=[],
        ),
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
