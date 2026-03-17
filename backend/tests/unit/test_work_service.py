from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.modules.works.schemas import WorkClose, WorkCreate, WorkReopen, WorkUpdateStatus
from app.modules.works.service import WorkService


@dataclass
class FakeClient:
    id: str
    name: str
    legal_name: str | None = None
    legal_address: str | None = None
    inn: str | None = None
    kpp: str | None = None
    signer_name: str | None = None
    contract_number: str | None = None
    contract_date: object | None = None
    address: str | None = None
    phone: str | None = None
    default_price_adjustment_percent: Decimal = Decimal("0.00")
    catalog_prices: list[object] = field(default_factory=list)


@dataclass
class FakeExecutor:
    id: str
    full_name: str
    hourly_rate: Decimal
    payment_category: object | None = None


@dataclass
class FakeMaterial:
    id: str
    name: str
    average_price: Decimal


@dataclass
class FakeWork:
    order_number: str
    client_id: str
    executor_id: str | None
    work_type: str
    doctor_id: str | None = None
    work_catalog_item_id: str | None = None
    description: str | None = None
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
    tooth_selection: list[dict[str, object]] | None = None
    status: str = "new"
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deadline_at: datetime | None = None
    delivery_sent: bool = False
    delivery_sent_at: datetime | None = None
    base_price_for_client: Decimal = Decimal("0.00")
    price_adjustment_percent: Decimal = Decimal("0.00")
    price_for_client: Decimal = Decimal("0.00")
    cost_price: Decimal = Decimal("0.00")
    margin: Decimal = Decimal("0.00")
    additional_expenses: Decimal = Decimal("0.00")
    labor_hours: Decimal = Decimal("0.00")
    labor_cost: Decimal = Decimal("0.00")
    amount_paid: Decimal = Decimal("0.00")
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    client: FakeClient | None = None
    executor: FakeExecutor | None = None
    doctor: object | None = None
    catalog_item: object | None = None
    work_items: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    work_operations: list = field(default_factory=list)
    attachments: list = field(default_factory=list)
    change_logs: list = field(default_factory=list)
    completed_at: datetime | None = None
    closed_at: datetime | None = None


@dataclass
class FakeWorkMaterial:
    material_id: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    work_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    material: FakeMaterial | None = None


@dataclass
class FakeWorkItem:
    work_type: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    sort_order: int
    work_catalog_item_id: str | None = None
    description: str | None = None
    work_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    catalog_item: object | None = None


@dataclass
class FakeWorkChangeLog:
    work_id: str
    action: str
    actor_email: str | None
    details: dict[str, object]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FakeOperationRate:
    executor_category_id: str
    labor_rate: Decimal
    executor_category: object | None = None


@dataclass
class FakeOperationCatalog:
    id: str
    code: str
    name: str
    payment_rates: list[FakeOperationRate]


@dataclass
class FakeWorkOperation:
    operation_id: str | None
    operation_code: str | None
    operation_name: str
    quantity: Decimal
    unit_labor_cost: Decimal
    total_labor_cost: Decimal
    executor_id: str | None = None
    executor_category_id: str | None = None
    status: str = "planned"
    sort_order: int = 0
    manual_rate_override: bool = False
    note: str | None = None
    work_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executor: FakeExecutor | None = None
    executor_category: object | None = None
    logs: list = field(default_factory=list)


@dataclass
class FakeWorkOperationLog:
    work_operation_id: str
    action: str
    actor_email: str | None
    details: dict[str, object]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FakeWorkRepository:
    def __init__(self, *, client: FakeClient, executor: FakeExecutor, material: FakeMaterial):
        self.client = client
        self.executor = executor
        self.material = material
        self.works: dict[str, FakeWork] = {}
        self.order_numbers: dict[str, str] = {}
        self.payroll_rows: list[tuple[str, str, int, Decimal, Decimal]] = []

    async def get(self, work_id: str):
        return self.works.get(work_id)

    async def get_by_order_number(self, order_number: str):
        work_id = self.order_numbers.get(order_number)
        return self.works.get(work_id) if work_id else None

    async def add(self, work):
        fake = FakeWork(
            order_number=work.order_number,
            client_id=work.client_id,
            executor_id=work.executor_id,
            doctor_id=getattr(work, "doctor_id", None),
            work_catalog_item_id=getattr(work, "work_catalog_item_id", None),
            work_type=work.work_type,
            description=work.description,
            doctor_name=work.doctor_name,
            doctor_phone=getattr(work, "doctor_phone", None),
            patient_name=work.patient_name,
            patient_age=getattr(work, "patient_age", None),
            patient_gender=getattr(work, "patient_gender", None),
            require_color_photo=getattr(work, "require_color_photo", False),
            face_shape=getattr(work, "face_shape", None),
            implant_system=getattr(work, "implant_system", None),
            metal_type=getattr(work, "metal_type", None),
            shade_color=getattr(work, "shade_color", None),
            tooth_formula=work.tooth_formula,
            tooth_selection=work.tooth_selection,
            status=work.status,
            received_at=work.received_at,
            deadline_at=work.deadline_at,
            delivery_sent=getattr(work, "delivery_sent", False),
            delivery_sent_at=getattr(work, "delivery_sent_at", None),
            base_price_for_client=work.base_price_for_client,
            price_adjustment_percent=work.price_adjustment_percent,
            price_for_client=work.price_for_client,
            cost_price=work.cost_price,
            margin=work.margin,
            additional_expenses=work.additional_expenses,
            labor_hours=work.labor_hours,
            labor_cost=work.labor_cost,
            amount_paid=work.amount_paid,
            client=self.client,
            executor=self.executor,
        )
        self.works[fake.id] = fake
        self.order_numbers[fake.order_number] = fake.id
        return fake

    async def add_material_usage(self, work_material):
        work = self.works[work_material.work_id]
        fake = FakeWorkMaterial(
            material_id=work_material.material_id,
            quantity=work_material.quantity,
            unit_cost=work_material.unit_cost,
            total_cost=work_material.total_cost,
            work_id=work_material.work_id,
            material=self.material,
        )
        work.materials.append(fake)
        return fake

    async def add_work_item(self, work_item):
        work = self.works[work_item.work_id]
        fake = FakeWorkItem(
            work_catalog_item_id=work_item.work_catalog_item_id,
            work_type=work_item.work_type,
            description=work_item.description,
            quantity=work_item.quantity,
            unit_price=work_item.unit_price,
            total_price=work_item.total_price,
            sort_order=work_item.sort_order,
            work_id=work_item.work_id,
            catalog_item=getattr(work_item, "catalog_item", None),
        )
        work.work_items.append(fake)
        return fake

    async def add_change_log(self, work_change_log):
        work = self.works[work_change_log.work_id]
        fake = FakeWorkChangeLog(
            work_id=work_change_log.work_id,
            action=work_change_log.action,
            actor_email=work_change_log.actor_email,
            details=work_change_log.details,
        )
        work.change_logs.insert(0, fake)
        return fake

    async def get_executor_payroll_summary(self, *, date_from, date_to, executor_id=None):
        return self.payroll_rows


class FakeClientRepository:
    def __init__(self, client: FakeClient):
        self.client = client

    async def get(self, client_id: str):
        return self.client if self.client.id == client_id else None


class FakeExecutorRepository:
    def __init__(self, executor: FakeExecutor):
        self.executor = executor

    async def get(self, executor_id: str):
        return self.executor if self.executor.id == executor_id else None


class FakeDoctorRepository:
    async def get(self, doctor_id: str):
        return None


class FakeWorkCatalogRepository:
    def __init__(self):
        self.items: dict[str, object] = {}

    async def get(self, item_id: str):
        return self.items.get(item_id)


class FakeMaterialRepository:
    def __init__(self, material: FakeMaterial):
        self.material = material
        self.consumed: list[tuple[str, Decimal]] = []

    async def list_by_ids(self, material_ids):
        return [self.material] if self.material.id in material_ids else []

    async def consume_stock(self, material_id: str, quantity: Decimal):
        self.consumed.append((material_id, quantity))


class FakeOperationRepository:
    def __init__(self, *, executor: FakeExecutor):
        self.executor = executor
        self.catalog_operations: dict[str, FakeOperationCatalog] = {}

    async def list_operations_by_ids(self, ids):
        return [self.catalog_operations[item_id] for item_id in ids if item_id in self.catalog_operations]

    async def add_work_operation(self, work_operation):
        work = self.work_repository.works[work_operation.work_id]
        fake = FakeWorkOperation(
            operation_id=work_operation.operation_id,
            operation_code=work_operation.operation_code,
            operation_name=work_operation.operation_name,
            quantity=work_operation.quantity,
            unit_labor_cost=work_operation.unit_labor_cost,
            total_labor_cost=work_operation.total_labor_cost,
            executor_id=work_operation.executor_id,
            executor_category_id=work_operation.executor_category_id,
            status=work_operation.status,
            sort_order=work_operation.sort_order,
            manual_rate_override=work_operation.manual_rate_override,
            note=work_operation.note,
            work_id=work_operation.work_id,
            executor=self.executor if work_operation.executor_id == self.executor.id else None,
            executor_category=self.executor.payment_category,
        )
        work.work_operations.append(fake)
        return fake

    async def add_work_operation_log(self, log):
        for work in self.work_repository.works.values():
            operation = next((item for item in work.work_operations if item.id == log.work_operation_id), None)
            if operation is None:
                continue
            operation.logs.insert(
                0,
                FakeWorkOperationLog(
                    work_operation_id=log.work_operation_id,
                    action=log.action,
                    actor_email=log.actor_email,
                    details=log.details,
                ),
            )
            return operation.logs[0]
        return None


class FakeContextUoW:
    def __init__(self, *, client: FakeClient, executor: FakeExecutor, material: FakeMaterial):
        self.clients = FakeClientRepository(client)
        self.executors = FakeExecutorRepository(executor)
        self.doctors = FakeDoctorRepository()
        self.materials = FakeMaterialRepository(material)
        self.work_catalog = FakeWorkCatalogRepository()
        self.works = FakeWorkRepository(client=client, executor=executor, material=material)
        self.operations = FakeOperationRepository(executor=executor)
        self.operations.work_repository = self.works
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


class FakeSearchService:
    def __init__(self):
        self.calls = []

    async def index_document(self, index, document_id, payload):
        self.calls.append((index, document_id, payload))


class FakeCacheService:
    def __init__(self):
        self.invalidated = []

    async def invalidate_prefix(self, prefix):
        self.invalidated.append(prefix)


@pytest.mark.asyncio
async def test_create_work_applies_client_adjustment_and_creates_change_log():
    client = FakeClient(id=str(uuid4()), name="Smile Studio", default_price_adjustment_percent=Decimal("-10.00"))
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    search = FakeSearchService()
    cache = FakeCacheService()
    service = WorkService(uow=uow, search=search, cache=cache)

    result = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-001",
            client_id=client.id,
            executor_id=executor.id,
            work_type="Коронка",
            patient_name="Ирина Соколова",
            doctor_name="Сергей Волков",
            doctor_phone="+79991112233",
            patient_age=34,
            patient_gender="female",
            require_color_photo=True,
            face_shape="oval",
            implant_system="Straumann",
            metal_type="Цирконий",
            shade_color="A2",
            tooth_selection=[{"tooth_code": "16", "state": "target", "surfaces": ["occlusal"]}],
            received_at=datetime.now(timezone.utc),
            base_price_for_client=Decimal("10000.00"),
            labor_hours=Decimal("2.00"),
            additional_expenses=Decimal("500.00"),
            materials=[{"material_id": material.id, "quantity": Decimal("1.000")}],
        ),
        actor_email="admin@dentallab.app",
    )

    assert uow.committed is True
    assert result.price_adjustment_percent == Decimal("-10.00")
    assert result.price_for_client == Decimal("9000.00")
    assert result.labor_cost == Decimal("5000.00")
    assert result.balance_due == Decimal("9000.00")
    assert result.tooth_formula == "16 (Oc)"
    assert result.tooth_selection[0].tooth_code == "16"
    assert result.doctor_phone == "+79991112233"
    assert result.patient_gender == "female"
    assert result.face_shape == "oval"
    assert result.change_logs[0].action == "created"
    assert result.change_logs[0].actor_email == "admin@dentallab.app"
    assert search.calls
    assert cache.invalidated == ["dashboard:"]


@pytest.mark.asyncio
async def test_get_payroll_summary_aggregates_repository_rows():
    client = FakeClient(id=str(uuid4()), name="Smile Studio")
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    uow.works.payroll_rows = [
        (executor.id, executor.full_name, 3, Decimal("12500.00"), Decimal("48000.00")),
    ]
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    summary = await service.get_payroll_summary(date_from=None, date_to=None, executor_id=None)

    assert summary.total_earnings == Decimal("12500.00")
    assert summary.total_revenue == Decimal("48000.00")
    assert summary.items[0].executor_name == "Dmitry Ivanov"


@pytest.mark.asyncio
async def test_create_work_uses_operation_catalog_rate_for_executor_category():
    payment_category = SimpleNamespace(id=str(uuid4()), code="ceramist_a", name="Керамист A")
    client = FakeClient(id=str(uuid4()), name="Smile Studio", default_price_adjustment_percent=Decimal("0.00"))
    executor = FakeExecutor(
        id=str(uuid4()),
        full_name="Dmitry Ivanov",
        hourly_rate=Decimal("2500.00"),
        payment_category=payment_category,
    )
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    operation = FakeOperationCatalog(
        id=str(uuid4()),
        code="CROWN_ZR",
        name="Циркониевая коронка",
        payment_rates=[
            FakeOperationRate(
                executor_category_id=payment_category.id,
                labor_rate=Decimal("3200.00"),
                executor_category=payment_category,
            )
        ],
    )
    uow.operations.catalog_operations[operation.id] = operation
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    result = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-002",
            client_id=client.id,
            executor_id=executor.id,
            work_type="Коронка",
            received_at=datetime.now(timezone.utc),
            base_price_for_client=Decimal("12000.00"),
            additional_expenses=Decimal("500.00"),
            operations=[
                {
                    "operation_id": operation.id,
                    "quantity": Decimal("2.00"),
                }
            ],
        )
    )

    assert result.labor_cost == Decimal("6400.00")
    assert result.operations[0].operation_code == "CROWN_ZR"
    assert result.operations[0].executor_category_name == "Керамист A"
    assert result.operations[0].total_labor_cost == Decimal("6400.00")


@pytest.mark.asyncio
async def test_create_work_uses_client_specific_catalog_price_without_default_adjustment():
    client = FakeClient(id=str(uuid4()), name="Smile Studio", default_price_adjustment_percent=Decimal("-7.50"))
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    catalog_item = SimpleNamespace(
        id=str(uuid4()),
        code="CAT-001",
        name="Циркониевая коронка",
        category="Ортопедия",
        base_price=Decimal("15000.00"),
        default_duration_hours=Decimal("3.00"),
        default_operations=[],
    )
    client.catalog_prices = [
        SimpleNamespace(
            work_catalog_item_id=catalog_item.id,
            price=Decimal("13200.00"),
        )
    ]
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    uow.work_catalog.items[catalog_item.id] = catalog_item
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    result = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-003",
            client_id=client.id,
            executor_id=executor.id,
            work_catalog_item_id=catalog_item.id,
            received_at=datetime.now(timezone.utc),
            labor_hours=Decimal("2.00"),
            additional_expenses=Decimal("500.00"),
        )
    )

    assert result.work_type == "Циркониевая коронка"
    assert result.base_price_for_client == Decimal("13200.00")
    assert result.price_adjustment_percent == Decimal("0.00")
    assert result.price_for_client == Decimal("13200.00")
    assert len(result.work_items) == 1
    assert result.work_items[0].work_type == "Циркониевая коронка"
    assert result.work_items[0].total_price == Decimal("13200.00")


@pytest.mark.asyncio
async def test_create_work_builds_multiple_work_items_and_aggregates_total():
    client = FakeClient(id=str(uuid4()), name="Smile Studio", default_price_adjustment_percent=Decimal("-7.50"))
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    primary_catalog_item = SimpleNamespace(
        id=str(uuid4()),
        code="CAT-001",
        name="Циркониевая коронка",
        category="Ортопедия",
        description="Основная реставрация",
        base_price=Decimal("15000.00"),
        default_duration_hours=Decimal("3.00"),
        default_operations=[],
    )
    extra_catalog_item = SimpleNamespace(
        id=str(uuid4()),
        code="CAT-002",
        name="Временная коронка",
        category="Ортопедия",
        description="Временная конструкция",
        base_price=Decimal("2500.00"),
        default_duration_hours=Decimal("1.00"),
        default_operations=[],
    )
    client.catalog_prices = [
        SimpleNamespace(
            work_catalog_item_id=primary_catalog_item.id,
            price=Decimal("13200.00"),
        )
    ]
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    uow.work_catalog.items[primary_catalog_item.id] = primary_catalog_item
    uow.work_catalog.items[extra_catalog_item.id] = extra_catalog_item
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    result = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-004",
            client_id=client.id,
            executor_id=executor.id,
            received_at=datetime.now(timezone.utc),
            additional_expenses=Decimal("500.00"),
            labor_hours=Decimal("2.00"),
            work_items=[
                {
                    "work_catalog_item_id": primary_catalog_item.id,
                    "quantity": Decimal("1.00"),
                    "unit_price": Decimal("13200.00"),
                },
                {
                    "work_catalog_item_id": extra_catalog_item.id,
                    "description": "Временная защита на период примерок",
                    "quantity": Decimal("2.00"),
                    "unit_price": Decimal("1800.00"),
                },
            ],
        )
    )

    assert result.work_type == "Циркониевая коронка"
    assert result.price_adjustment_percent == Decimal("0.00")
    assert result.base_price_for_client == Decimal("16800.00")
    assert result.price_for_client == Decimal("16800.00")
    assert len(result.work_items) == 2
    assert result.work_items[1].work_type == "Временная коронка"
    assert result.work_items[1].total_price == Decimal("3600.00")


@pytest.mark.asyncio
async def test_update_status_does_not_close_work_automatically():
    client = FakeClient(id=str(uuid4()), name="Smile Studio")
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    created = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-005",
            client_id=client.id,
            executor_id=executor.id,
            work_type="Коронка",
            received_at=datetime.now(timezone.utc),
            base_price_for_client=Decimal("12000.00"),
        )
    )

    updated = await service.update_status(
        str(created.id),
        WorkUpdateStatus(status="completed"),
        actor_email="admin@dentallab.app",
    )

    assert updated.status == "completed"
    assert updated.completed_at is not None
    assert updated.closed_at is None


@pytest.mark.asyncio
async def test_close_and_reopen_work_manage_closed_at_separately():
    client = FakeClient(id=str(uuid4()), name="Smile Studio")
    executor = FakeExecutor(id=str(uuid4()), full_name="Dmitry Ivanov", hourly_rate=Decimal("2500.00"))
    material = FakeMaterial(id=str(uuid4()), name="Zircon Disc", average_price=Decimal("3000.00"))
    uow = FakeContextUoW(client=client, executor=executor, material=material)
    service = WorkService(uow=uow, search=FakeSearchService(), cache=FakeCacheService())

    created = await service.create_work(
        WorkCreate(
            order_number="DL-TEST-006",
            client_id=client.id,
            executor_id=executor.id,
            work_type="Коронка",
            received_at=datetime.now(timezone.utc),
            base_price_for_client=Decimal("12000.00"),
        )
    )

    closed = await service.close_work(
        str(created.id),
        WorkClose(status="completed", note="close"),
        actor_email="admin@dentallab.app",
    )
    reopened = await service.reopen_work(
        str(created.id),
        WorkReopen(status="in_review", note="reopen"),
        actor_email="admin@dentallab.app",
    )

    assert closed.closed_at is not None
    assert closed.is_closed is True
    assert reopened.closed_at is None
    assert reopened.is_closed is False
    assert reopened.status == "in_review"
