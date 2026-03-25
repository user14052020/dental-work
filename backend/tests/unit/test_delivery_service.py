from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.delivery.schemas import DeliveryMarkSentPayload
from app.modules.delivery.service import DeliveryService


def build_narad(*, status: str = "completed", delivery_sent: bool = False):
    client = SimpleNamespace(
        id=str(uuid4()),
        name="Клиника Улыбка",
        address="Екатеринбург, ул. Белинского, 86",
        phone="+79991234567",
        contact_person="Анна Петрова",
        delivery_address="Екатеринбург, ул. Белинского, 86",
        delivery_contact="Марина Алексеева",
        delivery_phone="+79991230001",
    )
    executor = SimpleNamespace(id=str(uuid4()), full_name="Дмитрий Иванов")
    now = datetime.now(timezone.utc)
    work = SimpleNamespace(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        status=status,
        client_id=client.id,
        client=client,
        executor_id=executor.id,
        executor=executor,
        doctor_name="Сергей Волков",
        patient_name="Ирина Соколова",
        received_at=now,
        deadline_at=now,
        completed_at=now,
        closed_at=None,
        delivery_sent=delivery_sent,
        delivery_sent_at=None,
        price_for_client=Decimal("15500.00"),
        description="Тест",
        materials=[],
        work_operations=[],
        attachments=[],
        change_logs=[],
    )
    narad = SimpleNamespace(
        id=str(uuid4()),
        created_at=now,
        updated_at=now,
        narad_number="NAR-2026-0001",
        title="Циркониевая реставрация",
        status=status,
        client_id=client.id,
        client=client,
        doctor_name="Сергей Волков",
        patient_name="Ирина Соколова",
        received_at=now,
        deadline_at=now,
        completed_at=now if status in {"completed", "delivered"} else None,
        works=[work],
    )
    work.narad_id = narad.id
    work.narad = narad
    return narad


class FakeNaradRepository:
    def __init__(self, narads):
        self._narads = {narad.id: narad for narad in narads}
        self.last_list_kwargs = None

    async def list_for_delivery(self, **kwargs):
        self.last_list_kwargs = kwargs
        items = list(self._narads.values())
        sent = kwargs.get("sent")
        if sent is True:
            items = [item for item in items if all(work.delivery_sent for work in item.works)]
        elif sent is False:
            items = [item for item in items if any(not work.delivery_sent for work in item.works)]
        return items, len(items)

    async def list_for_delivery_by_ids(self, narad_ids):
        return [self._narads[narad_id] for narad_id in narad_ids if narad_id in self._narads]


class FakeWorkRepository:
    def __init__(self, narads):
        self._works = {work.id: work for narad in narads for work in narad.works}
        self.change_logs = []

    async def list_by_ids(self, work_ids):
        return [self._works[work_id] for work_id in work_ids if work_id in self._works]

    async def add_change_log(self, work_change_log):
        self.change_logs.append(work_change_log)
        return work_change_log


class FakeOrganizationRepository:
    def __init__(self, profile):
        self._profile = profile

    async def get_profile(self):
        return self._profile


class FakeContextUow:
    def __init__(self, narads, organization):
        self.narads = FakeNaradRepository(narads)
        self.works = FakeWorkRepository(narads)
        self.organization = FakeOrganizationRepository(organization)
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


class FakeSearchService:
    def __init__(self):
        self.index_calls = []

    async def search_works(self, query: str):
        return []

    async def index_document(self, index, document_id, payload):
        self.index_calls.append((index, document_id, payload))


class FakeCacheService:
    def __init__(self):
        self.invalidated = []

    async def invalidate_prefix(self, prefix):
        self.invalidated.append(prefix)


@pytest.mark.asyncio
async def test_mark_sent_updates_delivery_state_and_indexes():
    narad = build_narad()
    work = narad.works[0]
    organization = SimpleNamespace(display_name="ООО Северный Мост", legal_name="ООО Северный Мост", phone="+7999")
    uow = FakeContextUow([narad], organization)
    search = FakeSearchService()
    cache = FakeCacheService()
    service = DeliveryService(uow=uow, search=search, cache=cache)

    result = await service.mark_sent(
        DeliveryMarkSentPayload(narad_ids=[narad.id]),
        actor_email="admin@dentallab.app",
    )

    assert uow.committed is True
    assert result.updated_count == 1
    assert work.delivery_sent is True
    assert work.status == "delivered"
    assert narad.status == "delivered"
    assert work.closed_at is None
    assert len(search.index_calls) == 1
    assert cache.invalidated == ["dashboard:"]


@pytest.mark.asyncio
async def test_render_manifest_includes_delivery_data():
    narad = build_narad()
    organization = SimpleNamespace(
        display_name="ООО Северный Мост",
        legal_name="ООО Северный Мост",
        phone="+79995554433",
        mailing_address="Екатеринбург, ул. Луначарского, 80",
        legal_address="Екатеринбург, ул. Луначарского, 80",
    )
    uow = FakeContextUow([narad], organization)
    service = DeliveryService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    html = await service.render_manifest([narad.id])

    assert "Лист доставки" in html
    assert "Клиника Улыбка" in html
    assert "Марина Алексеева" in html
    assert "NAR-2026-0001" in html
    assert "15 500,00" in html


@pytest.mark.asyncio
async def test_list_delivery_items_passes_sorting_to_repository():
    narad = build_narad()
    organization = SimpleNamespace(display_name="ООО Северный Мост")
    uow = FakeContextUow([narad], organization)
    service = DeliveryService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    await service.list_delivery_items(
        page=1,
        page_size=10,
        search=None,
        client_id=None,
        executor_id=None,
        sent=False,
        sort_by="client_name",
        sort_direction="desc",
    )

    assert uow.narads.last_list_kwargs["sort_by"] == "client_name"
    assert uow.narads.last_list_kwargs["sort_direction"] == "desc"
