from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError
from app.db.models.inventory_adjustment import InventoryAdjustment, InventoryAdjustmentItem
from app.db.models.material import Material
from app.modules.inventory_adjustments.schemas import InventoryAdjustmentCreate
from app.modules.inventory_adjustments.service import InventoryAdjustmentService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class FakeMaterialRepository:
    def __init__(self, materials: list[Material]):
        self.materials = {material.id: material for material in materials}
        self.change_calls: list[tuple[str, Decimal, str, str | None]] = []

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
        inventory_adjustment_id: str | None = None,
        respect_reservations: bool = True,
    ) -> Material:
        material = self.materials[material_id]
        material.stock = (material.stock + quantity_delta).quantize(Decimal("0.001"))
        self.change_calls.append((material_id, quantity_delta, movement_type, inventory_adjustment_id))
        return material


class FakeInventoryAdjustmentRepository:
    def __init__(self):
        self.adjustments: dict[str, InventoryAdjustment] = {}

    async def add(self, adjustment: InventoryAdjustment) -> InventoryAdjustment:
        if getattr(adjustment, "id", None) is None:
            adjustment.id = str(uuid4())
        adjustment.created_at = getattr(adjustment, "created_at", None) or now_utc()
        adjustment.updated_at = getattr(adjustment, "updated_at", None) or now_utc()
        adjustment.items = getattr(adjustment, "items", [])
        self.adjustments[adjustment.id] = adjustment
        return adjustment

    async def add_item(self, item: InventoryAdjustmentItem) -> InventoryAdjustmentItem:
        adjustment = self.adjustments[item.adjustment_id]
        if getattr(item, "id", None) is None:
            item.id = str(uuid4())
        item.created_at = getattr(item, "created_at", None) or now_utc()
        item.updated_at = getattr(item, "updated_at", None) or now_utc()
        adjustment.items.append(item)
        return item

    async def get(self, adjustment_id: str) -> InventoryAdjustment | None:
        return self.adjustments.get(adjustment_id)

    async def get_by_number(self, adjustment_number: str) -> InventoryAdjustment | None:
        return next(
            (adjustment for adjustment in self.adjustments.values() if adjustment.adjustment_number == adjustment_number),
            None,
        )

    async def list(self, **kwargs):
        items = list(self.adjustments.values())
        return items, len(items)


class FakeContextUow:
    def __init__(self, materials: list[Material]):
        self.materials = FakeMaterialRepository(materials)
        self.inventory_adjustments = FakeInventoryAdjustmentRepository()
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

    async def index_document(self, *args):
        self.calls.append(args)


class FakeCacheService:
    def __init__(self):
        self.invalidated = []

    async def invalidate_prefix(self, prefix: str):
        self.invalidated.append(prefix)


@pytest.mark.asyncio
async def test_create_inventory_adjustment_updates_stock_and_returns_document():
    material = Material(
        id=str(uuid4()),
        name="Циркониевый диск",
        category="Керамика",
        unit="piece",
        stock=Decimal("10.000"),
        reserved_stock=Decimal("1.000"),
        purchase_price=Decimal("900.00"),
        average_price=Decimal("1200.00"),
        min_stock=Decimal("2.000"),
    )
    uow = FakeContextUow([material])
    search = FakeSearchService()
    cache = FakeCacheService()
    service = InventoryAdjustmentService(uow=uow, cache=cache, search=search)

    result = await service.create_adjustment(
        InventoryAdjustmentCreate(
            adjustment_number="INV-2026-0001",
            recorded_at=now_utc(),
            comment="Плановая инвентаризация",
            items=[
                {
                    "material_id": material.id,
                    "actual_stock": Decimal("8.500"),
                    "comment": "Недостача после пересчета",
                }
            ],
        )
    )

    assert uow.committed is True
    assert material.stock == Decimal("8.500")
    assert result.adjustment_number == "INV-2026-0001"
    assert result.changed_items_count == 1
    assert result.negative_delta_total == Decimal("1.500")
    assert result.items[0].material_name == "Циркониевый диск"
    assert uow.materials.change_calls[0][1] == Decimal("-1.500")
    assert search.calls
    assert cache.invalidated == ["dashboard:"]


@pytest.mark.asyncio
async def test_create_inventory_adjustment_rejects_actual_stock_below_reserved():
    material = Material(
        id=str(uuid4()),
        name="Циркониевый диск",
        category="Керамика",
        unit="piece",
        stock=Decimal("10.000"),
        reserved_stock=Decimal("2.000"),
        purchase_price=Decimal("900.00"),
        average_price=Decimal("1200.00"),
        min_stock=Decimal("2.000"),
    )
    uow = FakeContextUow([material])
    service = InventoryAdjustmentService(uow=uow, cache=FakeCacheService(), search=FakeSearchService())

    with pytest.raises(ConflictError):
        await service.create_adjustment(
            InventoryAdjustmentCreate(
                adjustment_number="INV-2026-0001",
                recorded_at=now_utc(),
                items=[{"material_id": material.id, "actual_stock": Decimal("1.500")}],
            )
        )
