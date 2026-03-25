from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError
from app.modules.payments.schemas import PaymentCreate, PaymentReturnNaradAllocation, PaymentUpdate
from app.modules.payments.service import PaymentService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeClient:
    id: str
    name: str


@dataclass
class FakeNarad:
    id: str
    client_id: str
    narad_number: str
    title: str
    status: str = "new"
    received_at: datetime = field(default_factory=now_utc)
    deadline_at: datetime | None = None
    works: list = field(default_factory=list)


@dataclass
class FakeWork:
    id: str
    client_id: str
    order_number: str
    work_type: str
    price_for_client: Decimal
    amount_paid: Decimal
    client: FakeClient
    status: str = "completed"
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    received_at: datetime = field(default_factory=now_utc)
    deadline_at: datetime | None = None
    executor_id: str | None = None
    executor: object | None = None
    doctor_id: str | None = None
    doctor: object | None = None
    catalog_item: object | None = None
    narad_id: str | None = None
    narad: FakeNarad | None = None
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
    tooth_selection: list[dict[str, object]] = field(default_factory=list)
    completed_at: datetime | None = None
    closed_at: datetime | None = None
    delivery_sent: bool = False
    delivery_sent_at: datetime | None = None
    base_price_for_client: Decimal = Decimal("0.00")
    price_adjustment_percent: Decimal = Decimal("0.00")
    cost_price: Decimal = Decimal("0.00")
    margin: Decimal = Decimal("0.00")
    additional_expenses: Decimal = Decimal("0.00")
    labor_hours: Decimal = Decimal("0.00")
    labor_cost: Decimal = Decimal("0.00")
    work_items: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    work_operations: list = field(default_factory=list)
    attachments: list = field(default_factory=list)
    change_logs: list = field(default_factory=list)
    payment_allocations: list = field(default_factory=list)


@dataclass
class FakePaymentAllocation:
    payment_id: str
    work_id: str
    amount: Decimal
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    payment: object | None = None
    work: FakeWork | None = None


@dataclass
class FakePayment:
    payment_number: str
    client_id: str
    payment_date: datetime
    method: str
    amount: Decimal
    external_reference: str | None = None
    comment: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    client: FakeClient | None = None
    allocations: list[FakePaymentAllocation] = field(default_factory=list)


class FakeClientRepository:
    def __init__(self, clients: list[FakeClient]):
        self.clients = {client.id: client for client in clients}

    async def get(self, client_id: str):
        return self.clients.get(str(client_id))


class FakeNaradRepository:
    def __init__(self, narads: list[FakeNarad]):
        self.narads = {narad.id: narad for narad in narads}

    async def get(self, narad_id: str):
        return self.narads.get(str(narad_id))


class FakeWorkRepository:
    def __init__(self, works: list[FakeWork]):
        self.works = {work.id: work for work in works}

    async def get(self, work_id: str):
        return self.works.get(str(work_id))

    async def list_by_client(self, client_id: str):
        return [work for work in self.works.values() if work.client_id == client_id]

    async def list_by_ids(self, work_ids: list[str]):
        return [self.works[str(work_id)] for work_id in work_ids if str(work_id) in self.works]

    async def add_change_log(self, change_log):
        work = self.works[change_log.work_id]
        if getattr(change_log, "id", None) is None:
            change_log.id = str(uuid4())
        if getattr(change_log, "created_at", None) is None:
            change_log.created_at = now_utc()
        if getattr(change_log, "updated_at", None) is None:
            change_log.updated_at = now_utc()
        work.change_logs.append(change_log)
        return change_log


class FakePaymentRepository:
    def __init__(self, works_repo: FakeWorkRepository, clients_repo: FakeClientRepository):
        self.works_repo = works_repo
        self.clients_repo = clients_repo
        self.payments: dict[str, FakePayment] = {}

    async def add(self, payment):
        if getattr(payment, "id", None) is None:
            payment.id = str(uuid4())
        payment.created_at = getattr(payment, "created_at", None) or now_utc()
        payment.updated_at = getattr(payment, "updated_at", None) or now_utc()
        payment.__dict__["client"] = self.clients_repo.clients[payment.client_id]
        self.payments[str(payment.id)] = payment
        return payment

    async def flush(self):
        for payment in self.payments.values():
            normalized_allocations = []
            for allocation in payment.allocations:
                allocation.payment_id = payment.id
                if getattr(allocation, "id", None) is None:
                    allocation.id = str(uuid4())
                allocation.created_at = getattr(allocation, "created_at", None) or now_utc()
                allocation.updated_at = now_utc()
                allocation.__dict__["payment"] = payment
                allocation.__dict__["work"] = self.works_repo.works[str(allocation.work_id)]
                normalized_allocations.append(allocation)
            payment.allocations = normalized_allocations
        for work in self.works_repo.works.values():
            work.payment_allocations = [
                allocation
                for payment in self.payments.values()
                for allocation in payment.allocations
                if allocation.work_id == work.id
            ]

    async def get(self, payment_id: str):
        return self.payments.get(str(payment_id))

    async def get_by_number(self, payment_number: str):
        return next((payment for payment in self.payments.values() if payment.payment_number == payment_number), None)

    async def list(self, **kwargs):
        items = list(self.payments.values())
        return items, len(items)

    async def list_by_client(self, client_id: str, *, limit: int = 10):
        items = [payment for payment in self.payments.values() if payment.client_id == client_id]
        items.sort(key=lambda payment: payment.payment_date, reverse=True)
        return items[:limit]

    async def sum_allocations_by_work_ids(self, work_ids: list[str]):
        result: dict[str, Decimal] = {}
        for payment in self.payments.values():
            for allocation in payment.allocations:
                if allocation.work_id in work_ids:
                    result[allocation.work_id] = result.get(allocation.work_id, Decimal("0.00")) + allocation.amount
        return result

    async def sum_allocated_to_work(self, work_id: str, *, exclude_payment_id: str | None = None):
        total = Decimal("0.00")
        for payment in self.payments.values():
            if exclude_payment_id and payment.id == exclude_payment_id:
                continue
            for allocation in payment.allocations:
                if allocation.work_id == work_id:
                    total += allocation.amount
        return total

    async def delete(self, payment):
        self.payments.pop(str(payment.id), None)


class FakeContextUow:
    def __init__(self, clients: list[FakeClient], works: list[FakeWork], narads: list[FakeNarad] | None = None):
        self.clients = FakeClientRepository(clients)
        self.narads = FakeNaradRepository(narads or [])
        self.works = FakeWorkRepository(works)
        self.payments = FakePaymentRepository(self.works, self.clients)
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


def build_service(uow: FakeContextUow) -> PaymentService:
    service = PaymentService(uow=uow, cache=FakeCacheService(), search=FakeSearchService())

    async def noop(*args, **kwargs):
        return None

    service._after_payment_changed = noop  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_create_payment_syncs_work_amount_paid_and_logs_change():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("15500.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    uow = FakeContextUow([client], [work])
    service = build_service(uow)

    result = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("5000.00"),
            allocations=[{"work_id": work.id, "amount": Decimal("5000.00")}],
        ),
        actor_email="admin@dentallab.app",
    )

    assert uow.committed is True
    assert work.amount_paid == Decimal("5000.00")
    assert result.allocated_total == Decimal("5000.00")
    assert result.unallocated_total == Decimal("0.00")
    assert len(result.allocations) == 1
    assert work.change_logs[-1].action == "payment_allocation_added"


@pytest.mark.asyncio
async def test_update_payment_redistributes_allocations_between_works():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    first_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("15500.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    second_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0002",
        work_type="Временная коронка",
        price_for_client=Decimal("3200.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    uow = FakeContextUow([client], [first_work, second_work])
    service = build_service(uow)

    created = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("4000.00"),
            allocations=[{"work_id": first_work.id, "amount": Decimal("3000.00")}],
        )
    )

    updated = await service.update_payment(
        created.id,
        PaymentUpdate(
            amount=Decimal("4000.00"),
            allocations=[
                {"work_id": first_work.id, "amount": Decimal("2000.00")},
                {"work_id": second_work.id, "amount": Decimal("1500.00")},
            ],
        ),
        actor_email="admin@dentallab.app",
    )

    assert first_work.amount_paid == Decimal("2000.00")
    assert second_work.amount_paid == Decimal("1500.00")
    assert updated.allocated_total == Decimal("3500.00")
    assert updated.unallocated_total == Decimal("500.00")


@pytest.mark.asyncio
async def test_list_work_candidates_keeps_current_payment_allocation_available():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("10000.00"),
        amount_paid=Decimal("6000.00"),
        client=client,
    )
    uow = FakeContextUow([client], [work])
    service = build_service(uow)

    payment = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="card",
            amount=Decimal("2000.00"),
            allocations=[{"work_id": work.id, "amount": Decimal("2000.00")}],
        )
    )
    work.amount_paid = Decimal("6000.00")

    candidates = await service.list_work_candidates(client.id, payment_id=payment.id)

    assert len(candidates) == 1
    assert candidates[0].existing_allocation_amount == Decimal("2000.00")
    assert candidates[0].available_to_allocate == Decimal("6000.00")


@pytest.mark.asyncio
async def test_create_payment_rejects_overallocation_against_work_balance():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("10000.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    uow = FakeContextUow([client], [work])
    service = build_service(uow)

    await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("9500.00"),
            allocations=[{"work_id": work.id, "amount": Decimal("9500.00")}],
        )
    )

    with pytest.raises(ConflictError, match="remaining balance"):
        await service.create_payment(
            PaymentCreate(
                client_id=client.id,
                payment_date=now_utc(),
                method="cash",
                amount=Decimal("1000.00"),
                allocations=[{"work_id": work.id, "amount": Decimal("600.00")}],
            )
        )


@pytest.mark.asyncio
async def test_create_payment_from_narad_allocation_distributes_between_works():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    narad = FakeNarad(
        id=str(uuid4()),
        client_id=client.id,
        narad_number="NR-2026-0001",
        title="Комплексное восстановление",
    )
    first_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("4000.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    second_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0002",
        work_type="Временная коронка",
        price_for_client=Decimal("6000.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    narad.works = [first_work, second_work]
    uow = FakeContextUow([client], [first_work, second_work], [narad])
    service = build_service(uow)

    payment = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("5000.00"),
            narad_allocations=[{"narad_id": narad.id, "amount": Decimal("5000.00")}],
        )
    )

    assert first_work.amount_paid == Decimal("4000.00")
    assert second_work.amount_paid == Decimal("1000.00")
    assert len(payment.narad_allocations) == 1
    assert payment.narad_allocations[0].narad_id == narad.id
    assert payment.narad_allocations[0].amount == Decimal("5000.00")


@pytest.mark.asyncio
async def test_list_narad_candidates_returns_aggregated_balance():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    narad = FakeNarad(
        id=str(uuid4()),
        client_id=client.id,
        narad_number="NR-2026-0001",
        title="Комплексное восстановление",
    )
    first_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("4000.00"),
        amount_paid=Decimal("1500.00"),
        client=client,
    )
    second_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0002",
        work_type="Временная коронка",
        price_for_client=Decimal("6000.00"),
        amount_paid=Decimal("500.00"),
        client=client,
    )
    narad.works = [first_work, second_work]
    uow = FakeContextUow([client], [first_work, second_work], [narad])
    service = build_service(uow)

    candidates = await service.list_narad_candidates(client.id)

    assert len(candidates) == 1
    assert candidates[0].narad_id == narad.id
    assert candidates[0].total_price == Decimal("10000.00")
    assert candidates[0].amount_paid == Decimal("2000.00")
    assert candidates[0].balance_due == Decimal("8000.00")


@pytest.mark.asyncio
async def test_return_narad_allocation_restores_unallocated_balance():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    narad = FakeNarad(
        id=str(uuid4()),
        client_id=client.id,
        narad_number="NR-2026-0001",
        title="Комплексное восстановление",
    )
    first_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("4000.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    second_work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        narad_id=narad.id,
        narad=narad,
        order_number="DL-2026-0002",
        work_type="Временная коронка",
        price_for_client=Decimal("6000.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    narad.works = [first_work, second_work]
    uow = FakeContextUow([client], [first_work, second_work], [narad])
    service = build_service(uow)

    payment = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("7000.00"),
            narad_allocations=[{"narad_id": narad.id, "amount": Decimal("5000.00")}],
        )
    )

    result = await service.return_narad_allocation(
        payment.id,
        PaymentReturnNaradAllocation(narad_id=narad.id),
        actor_email="admin@dentallab.app",
    )

    assert first_work.amount_paid == Decimal("0.00")
    assert second_work.amount_paid == Decimal("0.00")
    assert result.allocated_total == Decimal("0.00")
    assert result.unallocated_total == Decimal("7000.00")
    assert result.narad_allocations == []


@pytest.mark.asyncio
async def test_delete_unallocated_balance_reduces_payment_amount_only():
    client = FakeClient(id=str(uuid4()), name="Клиника Улыбка")
    work = FakeWork(
        id=str(uuid4()),
        client_id=client.id,
        order_number="DL-2026-0001",
        work_type="Циркониевая коронка",
        price_for_client=Decimal("15500.00"),
        amount_paid=Decimal("0.00"),
        client=client,
    )
    uow = FakeContextUow([client], [work])
    service = build_service(uow)

    payment = await service.create_payment(
        PaymentCreate(
            client_id=client.id,
            payment_date=now_utc(),
            method="bank_transfer",
            amount=Decimal("7000.00"),
            allocations=[{"work_id": work.id, "amount": Decimal("5000.00")}],
        )
    )

    result = await service.delete_unallocated_balance(payment.id)

    assert work.amount_paid == Decimal("5000.00")
    assert result.amount == Decimal("5000.00")
    assert result.allocated_total == Decimal("5000.00")
    assert result.unallocated_total == Decimal("0.00")
