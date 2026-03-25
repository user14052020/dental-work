from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError
from app.modules.narads.schemas import NaradClose, NaradReopen, OutsideWorkMarkReturned, OutsideWorkMarkSent
from app.modules.narads.service import NaradService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeClient:
    id: str
    name: str


@dataclass
class FakeContractor:
    id: str
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    comment: str | None = None
    is_active: bool = True


@dataclass
class FakeMaterial:
    id: str
    name: str
    stock: Decimal
    reserved_stock: Decimal
    average_price: Decimal


@dataclass
class FakeWorkMaterial:
    material_id: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    material: FakeMaterial
    work_id: str | None = None
    reserved_at: datetime | None = None
    consumed_at: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)


@dataclass
class FakeWorkChangeLog:
    work_id: str
    action: str
    actor_email: str | None
    details: dict[str, object]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)


@dataclass
class FakeNaradStatusLog:
    narad_id: str
    action: str
    to_status: str
    actor_email: str | None = None
    from_status: str | None = None
    note: str | None = None
    details: dict[str, object] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)


@dataclass
class FakeWork:
    id: str
    narad_id: str
    client_id: str
    order_number: str
    work_type: str
    status: str
    price_for_client: Decimal
    cost_price: Decimal
    margin: Decimal
    amount_paid: Decimal
    received_at: datetime
    client: FakeClient
    description: str | None = None
    deadline_at: datetime | None = None
    completed_at: datetime | None = None
    closed_at: datetime | None = None
    executor_id: str | None = None
    executor: object | None = None
    doctor_id: str | None = None
    doctor: object | None = None
    doctor_name: str | None = None
    doctor_phone: str | None = None
    patient_name: str | None = None
    patient_age: int | None = None
    patient_gender: str | None = None
    require_color_photo: bool = False
    face_shape: str | None = None
    implant_system: str | None = None
    metal_type: str | None = None
    shade_color: str | None = None
    tooth_formula: str | None = None
    tooth_selection: list[dict[str, object]] = field(default_factory=list)
    catalog_item: object | None = None
    work_items: list[object] = field(default_factory=list)
    materials: list[FakeWorkMaterial] = field(default_factory=list)
    work_operations: list[object] = field(default_factory=list)
    attachments: list[object] = field(default_factory=list)
    change_logs: list[FakeWorkChangeLog] = field(default_factory=list)
    delivery_sent: bool = False
    delivery_sent_at: datetime | None = None
    base_price_for_client: Decimal = Decimal("0.00")
    price_adjustment_percent: Decimal = Decimal("0.00")
    additional_expenses: Decimal = Decimal("0.00")
    labor_hours: Decimal = Decimal("0.00")
    labor_cost: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    narad: object | None = None


@dataclass
class FakeNarad:
    id: str
    narad_number: str
    client_id: str
    title: str
    status: str
    received_at: datetime
    client: FakeClient
    description: str | None = None
    doctor_id: str | None = None
    doctor_name: str | None = None
    doctor_phone: str | None = None
    contractor_id: str | None = None
    contractor: object | None = None
    patient_name: str | None = None
    patient_age: int | None = None
    patient_gender: str | None = None
    require_color_photo: bool = False
    face_shape: str | None = None
    implant_system: str | None = None
    metal_type: str | None = None
    shade_color: str | None = None
    tooth_formula: str | None = None
    tooth_selection: list[dict[str, object]] = field(default_factory=list)
    deadline_at: datetime | None = None
    completed_at: datetime | None = None
    closed_at: datetime | None = None
    is_outside_work: bool = False
    outside_lab_name: str | None = None
    outside_order_number: str | None = None
    outside_cost: Decimal = Decimal("0.00")
    outside_sent_at: datetime | None = None
    outside_due_at: datetime | None = None
    outside_returned_at: datetime | None = None
    outside_comment: str | None = None
    works: list[FakeWork] = field(default_factory=list)
    status_logs: list[FakeNaradStatusLog] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)


class FakeNaradRepository:
    def __init__(self, narad: FakeNarad):
        self.narad = narad

    async def get(self, narad_id: str):
        return self.narad if self.narad.id == str(narad_id) else None

    async def add_status_log(self, log):
        fake = FakeNaradStatusLog(
            narad_id=log.narad_id,
            action=log.action,
            actor_email=log.actor_email,
            from_status=log.from_status,
            to_status=log.to_status,
            note=log.note,
            details=log.details,
        )
        self.narad.status_logs.insert(0, fake)
        return fake


class FakeWorkRepository:
    def __init__(self, work: FakeWork):
        self.work = work

    async def get(self, work_id: str):
        return self.work if self.work.id == str(work_id) else None

    async def add_change_log(self, change_log):
        fake = FakeWorkChangeLog(
            work_id=change_log.work_id,
            action=change_log.action,
            actor_email=change_log.actor_email,
            details=change_log.details,
        )
        self.work.change_logs.insert(0, fake)
        return fake


class FakeContractorRepository:
    def __init__(self, contractor: FakeContractor | None = None):
        self.contractor = contractor

    async def get(self, contractor_id: str):
        if self.contractor and self.contractor.id == str(contractor_id):
            return self.contractor
        return None


class FakeMaterialRepository:
    def __init__(self, material: FakeMaterial):
        self.material = material

    async def change_stock(
        self,
        material_id: str,
        *,
        quantity_delta: Decimal,
        movement_type: str,
        unit_cost: Decimal | None,
        comment: str | None = None,
        receipt_id: str | None = None,
        work_id: str | None = None,
        respect_reservations: bool = True,
    ):
        assert self.material.id == material_id
        self.material.stock = (self.material.stock + quantity_delta).quantize(Decimal("0.001"))
        return self.material

    async def change_reserved_stock(
        self,
        material_id: str,
        *,
        quantity_delta: Decimal,
        movement_type: str,
        comment: str | None = None,
        work_id: str | None = None,
    ):
        assert self.material.id == material_id
        self.material.reserved_stock = (self.material.reserved_stock + quantity_delta).quantize(Decimal("0.001"))
        return self.material


class FakePaymentRepository:
    async def list_by_narad(self, narad_id: str, limit: int = 20):
        return []


class FakeContextUow:
    def __init__(self, narad: FakeNarad, work: FakeWork, material: FakeMaterial, contractor: FakeContractor | None = None):
        self.narads = FakeNaradRepository(narad)
        self.works = FakeWorkRepository(work)
        self.contractors = FakeContractorRepository(contractor)
        self.materials = FakeMaterialRepository(material)
        self.payments = FakePaymentRepository()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


class FakeSearchService:
    async def index_document(self, *args, **kwargs):
        return None


class FakeCacheService:
    async def invalidate_prefix(self, *args, **kwargs):
        return None


def build_service(
    *,
    narad: FakeNarad,
    work: FakeWork,
    material: FakeMaterial,
    contractor: FakeContractor | None = None,
) -> NaradService:
    return NaradService(
        uow=FakeContextUow(narad, work, material, contractor),
        search=FakeSearchService(),
        cache=FakeCacheService(),
    )


def build_fixture():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    material = FakeMaterial(
        id=str(uuid4()),
        name="Циркониевый диск",
        stock=Decimal("10.000"),
        reserved_stock=Decimal("0.000"),
        average_price=Decimal("1200.00"),
    )
    narad = FakeNarad(
        id=str(uuid4()),
        narad_number="NAR-2026-0001",
        client_id=client.id,
        title="Наряд на ортопедию",
        status="in_progress",
        received_at=now_utc(),
        client=client,
    )
    work = FakeWork(
        id=str(uuid4()),
        narad_id=narad.id,
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        status="in_progress",
        price_for_client=Decimal("15000.00"),
        cost_price=Decimal("3400.00"),
        margin=Decimal("11600.00"),
        amount_paid=Decimal("0.00"),
        received_at=narad.received_at,
        client=client,
    )
    usage = FakeWorkMaterial(
        material_id=material.id,
        quantity=Decimal("2.000"),
        unit_cost=material.average_price,
        total_cost=Decimal("2400.00"),
        material=material,
        work_id=work.id,
    )
    work.materials.append(usage)
    work.narad = narad
    narad.works.append(work)
    return narad, work, material, usage


@pytest.mark.asyncio
async def test_reserve_close_and_reopen_narad_manage_materials():
    narad, work, material, usage = build_fixture()
    service = build_service(narad=narad, work=work, material=material)

    reserved = await service.reserve_materials(narad.id, actor_email="admin@dentallab.app")
    assert reserved.is_closed is False
    assert material.stock == Decimal("10.000")
    assert material.reserved_stock == Decimal("2.000")
    assert usage.reserved_at is not None
    assert usage.consumed_at is None
    assert narad.status_logs[0].action == "materials_reserved"

    closed = await service.close_narad(
        narad.id,
        NaradClose(status="completed", note="Закрываем заказ"),
        actor_email="admin@dentallab.app",
    )
    assert closed.is_closed is True
    assert material.stock == Decimal("8.000")
    assert material.reserved_stock == Decimal("0.000")
    assert usage.reserved_at is not None
    assert usage.consumed_at is not None
    assert work.closed_at is not None
    assert narad.closed_at is not None
    assert narad.status_logs[0].action == "closed"
    assert work.change_logs[0].action == "narad_closed"

    reopened = await service.reopen_narad(
        narad.id,
        NaradReopen(status="in_progress", note="Возвращаем в производство"),
        actor_email="admin@dentallab.app",
    )
    assert reopened.is_closed is False
    assert material.stock == Decimal("10.000")
    assert material.reserved_stock == Decimal("2.000")
    assert usage.consumed_at is None
    assert work.closed_at is None
    assert narad.closed_at is None
    assert narad.status == "in_progress"
    assert narad.status_logs[0].action == "reopened"
    assert work.change_logs[0].action == "narad_reopened"


@pytest.mark.asyncio
async def test_reserve_materials_rejects_closed_narad():
    narad, work, material, _usage = build_fixture()
    narad.status = "completed"
    narad.closed_at = now_utc()
    work.status = "completed"
    work.closed_at = narad.closed_at
    service = build_service(narad=narad, work=work, material=material)

    with pytest.raises(ConflictError, match="Closed narad cannot reserve materials"):
        await service.reserve_materials(narad.id, actor_email="admin@dentallab.app")


@pytest.mark.asyncio
async def test_mark_outside_sent_sets_fields_and_logs():
    narad, work, material, _usage = build_fixture()
    service = build_service(narad=narad, work=work, material=material)
    sent_at = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
    due_at = datetime(2026, 3, 28, 18, 0, tzinfo=timezone.utc)

    result = await service.mark_outside_sent(
        narad.id,
        payload=OutsideWorkMarkSent(
            outside_lab_name="Лаборатория Партнер",
            outside_order_number="EXT-2026-001",
            outside_cost=Decimal("4200.00"),
            outside_sent_at=sent_at,
            outside_due_at=due_at,
            outside_comment="Передано на облицовку",
        ),
        actor_email="admin@dentallab.app",
    )

    assert result.is_outside_work is True
    assert narad.is_outside_work is True
    assert narad.outside_lab_name == "Лаборатория Партнер"
    assert narad.outside_order_number == "EXT-2026-001"
    assert narad.outside_cost == Decimal("4200.00")
    assert narad.outside_sent_at == sent_at
    assert narad.outside_due_at == due_at
    assert narad.outside_returned_at is None
    assert narad.outside_comment == "Передано на облицовку"
    assert narad.status_logs[0].action == "outside_sent"
    assert work.change_logs[0].action == "outside_sent"


@pytest.mark.asyncio
async def test_mark_outside_returned_sets_return_date_and_logs():
    narad, work, material, _usage = build_fixture()
    sent_at = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)
    narad.is_outside_work = True
    narad.outside_lab_name = "Лаборатория Партнер"
    narad.outside_order_number = "EXT-2026-001"
    narad.outside_cost = Decimal("4200.00")
    narad.outside_sent_at = sent_at
    narad.outside_due_at = datetime(2026, 3, 28, 18, 0, tzinfo=timezone.utc)
    service = build_service(narad=narad, work=work, material=material)
    returned_at = datetime(2026, 3, 27, 16, 30, tzinfo=timezone.utc)

    result = await service.mark_outside_returned(
        narad.id,
        payload=OutsideWorkMarkReturned(
            outside_returned_at=returned_at,
            outside_comment="Вернулось после облицовки",
        ),
        actor_email="admin@dentallab.app",
    )

    assert result.outside_returned_at == returned_at
    assert narad.outside_returned_at == returned_at
    assert narad.outside_comment == "Вернулось после облицовки"
    assert narad.status_logs[0].action == "outside_returned"
    assert work.change_logs[0].action == "outside_returned"


@pytest.mark.asyncio
async def test_mark_outside_sent_uses_selected_contractor_snapshot():
    narad, work, material, _usage = build_fixture()
    contractor = FakeContractor(
        id=str(uuid4()),
        name="Лаборатория Партнер",
        contact_person="Алексей Новиков",
        phone="+79995550077",
    )
    service = build_service(narad=narad, work=work, material=material, contractor=contractor)
    sent_at = datetime(2026, 3, 25, 10, 0, tzinfo=timezone.utc)

    await service.mark_outside_sent(
        narad.id,
        payload=OutsideWorkMarkSent(
            contractor_id=contractor.id,
            outside_order_number="EXT-2026-001",
            outside_cost=Decimal("4200.00"),
            outside_sent_at=sent_at,
            outside_comment="Передано на облицовку",
        ),
        actor_email="admin@dentallab.app",
    )

    assert narad.contractor_id == contractor.id
    assert narad.outside_lab_name == contractor.name


@pytest.mark.asyncio
async def test_get_narad_includes_outside_cost_in_total_cost_and_margin():
    narad, work, material, _usage = build_fixture()
    narad.is_outside_work = True
    narad.outside_cost = Decimal("4200.00")
    service = build_service(narad=narad, work=work, material=material)

    result = await service.get_narad(narad.id)

    assert result.total_price == Decimal("15000.00")
    assert result.total_cost == Decimal("7600.00")
    assert result.total_margin == Decimal("7400.00")
