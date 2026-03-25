from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError
from app.db.models.material import Material
from app.modules.receipts.schemas import MaterialReceiptCreate
from app.modules.receipts.service import MaterialReceiptService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class FakeMaterialRepository:
    def __init__(self, materials: list[Material]):
        self.materials = {material.id: material for material in materials}

    async def list_by_ids(self, ids: list[str]) -> list[Material]:
        return [self.materials[material_id] for material_id in ids if material_id in self.materials]

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
    ) -> Material:
        material = self.materials[material_id]
        material.stock = (material.stock + quantity_delta).quantize(Decimal("0.001"))
        if unit_cost is not None:
            material.average_price = unit_cost.quantize(Decimal("0.01"))
        return material


class FakeReceiptRepository:
    def __init__(self):
        self.receipts: dict[str, object] = {}

    async def get(self, receipt_id: str):
        return self.receipts.get(receipt_id)

    async def get_by_number(self, receipt_number: str):
        return next(
            (receipt for receipt in self.receipts.values() if receipt.receipt_number == receipt_number),
            None,
        )

    async def add(self, receipt):
        if getattr(receipt, "id", None) is None:
            receipt.id = str(uuid4())
        receipt.created_at = getattr(receipt, "created_at", None) or now_utc()
        receipt.updated_at = getattr(receipt, "updated_at", None) or now_utc()
        self.receipts[receipt.id] = receipt
        return receipt

    async def add_item(self, item):
        receipt = self.receipts[item.receipt_id]
        if getattr(item, "id", None) is None:
            item.id = str(uuid4())
        item.created_at = getattr(item, "created_at", None) or now_utc()
        item.updated_at = getattr(item, "updated_at", None) or now_utc()
        item.material = None
        receipt.items.append(item)
        return item

    async def list(self, **kwargs):
        items = list(self.receipts.values())
        return items, len(items)


class FakeContextUow:
    def __init__(self, materials: list[Material]):
        self.materials = FakeMaterialRepository(materials)
        self.receipts = FakeReceiptRepository()
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


def build_service(uow: FakeContextUow) -> MaterialReceiptService:
    return MaterialReceiptService(uow=uow, cache=FakeCacheService(), search=FakeSearchService())


@pytest.mark.asyncio
async def test_create_receipt_updates_material_stock_and_totals():
    material = Material(
        id=str(uuid4()),
        name="Циркониевый диск",
        category="Керамика",
        unit="piece",
        stock=Decimal("0.000"),
        purchase_price=Decimal("0.00"),
        average_price=Decimal("0.00"),
        min_stock=Decimal("0.000"),
    )
    uow = FakeContextUow([material])
    service = build_service(uow)

    receipt = await service.create_receipt(
        MaterialReceiptCreate(
            receipt_number="RCPT-2026-0001",
            received_at=now_utc(),
            supplier="Дент Снаб",
            comment="Первичный приход",
            items=[
                {
                    "material_id": material.id,
                    "quantity": Decimal("2.500"),
                    "unit_price": Decimal("1450.00"),
                }
            ],
        )
    )

    assert uow.committed is True
    assert material.stock == Decimal("2.500")
    assert material.average_price == Decimal("1450.00")
    assert receipt.receipt_number == "RCPT-2026-0001"
    assert receipt.total_amount == Decimal("3625.00")
    assert receipt.total_quantity == Decimal("2.500")
    assert receipt.items[0].material_name == "Циркониевый диск"


@pytest.mark.asyncio
async def test_create_receipt_rejects_duplicate_number():
    material = Material(
        id=str(uuid4()),
        name="Циркониевый диск",
        category="Керамика",
        unit="piece",
        stock=Decimal("0.000"),
        purchase_price=Decimal("0.00"),
        average_price=Decimal("0.00"),
        min_stock=Decimal("0.000"),
    )
    uow = FakeContextUow([material])
    service = build_service(uow)

    payload = MaterialReceiptCreate(
        receipt_number="RCPT-2026-0001",
        received_at=now_utc(),
        supplier="Дент Снаб",
        items=[
            {
                "material_id": material.id,
                "quantity": Decimal("1.000"),
                "unit_price": Decimal("1000.00"),
            }
        ],
    )

    await service.create_receipt(payload)

    with pytest.raises(ConflictError):
        await service.create_receipt(payload)
