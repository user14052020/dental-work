from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.materials.schemas import ManualMaterialConsumptionUpdate
from app.modules.materials.service import MaterialService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeMaterial:
    id: str
    name: str = "Циркониевый диск"
    category: str | None = "Диски"
    unit: str = "piece"
    stock: Decimal = Decimal("10.000")
    reserved_stock: Decimal = Decimal("2.000")
    purchase_price: Decimal = Decimal("1000.00")
    average_price: Decimal = Decimal("1200.00")
    supplier: str | None = "Демо поставщик"
    min_stock: Decimal = Decimal("1.000")
    comment: str | None = None
    available_stock: Decimal = Decimal("8.000")
    is_low_stock: bool = False
    created_at: datetime = now_utc()
    updated_at: datetime = now_utc()


class FakeMaterialRepository:
    def __init__(self, material: FakeMaterial):
        self.material = material
        self.updated_payload: tuple[str, Decimal, str | None] | None = None
        self.deleted_movement_id: str | None = None

    async def list(self, *, page: int, page_size: int, search: str | None, low_stock_only: bool, ids=None):
        return [self.material], 1

    async def update_manual_consumption(self, movement_id: str, *, quantity: Decimal, reason: str | None = None):
        self.updated_payload = (movement_id, quantity, reason)
        self.material.stock = Decimal("12.500")
        return self.material

    async def delete_manual_consumption(self, movement_id: str):
        self.deleted_movement_id = movement_id
        self.material.stock = Decimal("13.000")
        return self.material


class FakeContextUow:
    def __init__(self, material: FakeMaterial):
        self.materials = FakeMaterialRepository(material)
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
async def test_update_manual_consumption_recalculates_material_read_model():
    material = FakeMaterial(id=str(uuid4()))
    uow = FakeContextUow(material)
    search = FakeSearchService()
    cache = FakeCacheService()
    service = MaterialService(uow=uow, cache=cache, search=search)

    result = await service.update_manual_consumption(
        str(uuid4()),
        ManualMaterialConsumptionUpdate(quantity=Decimal("1.500"), reason="Коррекция склада"),
    )

    assert uow.committed is True
    assert result.stock == Decimal("12.500")
    assert result.available_stock == Decimal("10.500")
    assert search.calls
    assert cache.invalidated == ["dashboard:"]


@pytest.mark.asyncio
async def test_delete_manual_consumption_recalculates_material_read_model():
    material = FakeMaterial(id=str(uuid4()))
    uow = FakeContextUow(material)
    search = FakeSearchService()
    cache = FakeCacheService()
    service = MaterialService(uow=uow, cache=cache, search=search)

    result = await service.delete_manual_consumption(str(uuid4()))

    assert uow.committed is True
    assert result.stock == Decimal("13.000")
    assert result.available_stock == Decimal("11.000")
    assert search.calls
    assert cache.invalidated == ["dashboard:"]


@pytest.mark.asyncio
async def test_list_materials_returns_computed_fields():
    material = FakeMaterial(id=str(uuid4()))
    uow = FakeContextUow(material)
    search = FakeSearchService()
    cache = FakeCacheService()
    service = MaterialService(uow=uow, cache=cache, search=search)

    result = await service.list_materials(page=1, page_size=10, search=None, low_stock_only=False)

    assert result.items[0].name == material.name
    assert result.items[0].reserved_stock == Decimal("2.000")
    assert result.items[0].available_stock == Decimal("8.000")
