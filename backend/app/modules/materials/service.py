from __future__ import annotations

from decimal import Decimal

from app.common.pagination import PaginatedResponse
from app.common.enums import StockMovementType
from app.common.search_documents import build_material_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.material import Material
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.materials.schemas import (
    MaterialConsume,
    MaterialCreate,
    MaterialDetailRead,
    MaterialListResponse,
    MaterialRead,
    ManualMaterialConsumptionUpdate,
    StockMovementRead,
    MaterialUpdate,
)


class MaterialService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService, search: SearchService):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_materials(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        low_stock_only: bool,
    ) -> MaterialListResponse:
        search_ids = await self._search.search_materials(search) if search else None
        async with self._uow as uow:
            materials, total_items = await uow.materials.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                low_stock_only=low_stock_only,
                ids=search_ids if search_ids else None,
            )
            items = [self._map_material_read(material) for material in materials]
        return PaginatedResponse[MaterialRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_material(self, material_id: str) -> MaterialDetailRead:
        async with self._uow as uow:
            material = await uow.materials.get(material_id)
            if material is None:
                raise NotFoundError("material", material_id)
            return self._map_material_detail(material)

    async def create_material(self, payload: MaterialCreate) -> MaterialRead:
        async with self._uow as uow:
            data = payload.model_dump()
            data["stock"] = Decimal("0.000")
            material = await uow.materials.add(Material(**data))
            if payload.stock > 0:
                material.purchase_price = payload.purchase_price
                material.average_price = payload.average_price
                await uow.materials.change_stock(
                    material.id,
                    quantity_delta=payload.stock,
                    movement_type=StockMovementType.OPENING_BALANCE.value,
                    unit_cost=payload.average_price,
                    comment="Начальный остаток при создании материала",
                )
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return self._map_material_read(material)

    async def update_material(self, material_id: str, payload: MaterialUpdate) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.get(material_id)
            if material is None:
                raise NotFoundError("material", material_id)
            data = payload.model_dump(exclude_unset=True)
            stock_target = data.pop("stock", None)
            for field, value in data.items():
                setattr(material, field, value)
            if stock_target is not None:
                quantity_delta = (stock_target - material.stock).quantize(Decimal("0.001"))
                if quantity_delta != Decimal("0.000"):
                    await uow.materials.change_stock(
                        material.id,
                        quantity_delta=quantity_delta,
                        movement_type=StockMovementType.ADJUSTMENT.value,
                        unit_cost=material.average_price,
                        comment="Ручная корректировка остатка из карточки материала",
                    )
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return self._map_material_read(material)

    async def consume_material(self, material_id: str, payload: MaterialConsume) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.change_stock(
                material_id,
                quantity_delta=-payload.quantity,
                movement_type=StockMovementType.CONSUME.value,
                unit_cost=None,
                comment=payload.reason or "Ручное списание со склада",
            )
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return self._map_material_read(material)

    async def update_manual_consumption(
        self,
        movement_id: str,
        payload: ManualMaterialConsumptionUpdate,
    ) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.update_manual_consumption(
                movement_id,
                quantity=payload.quantity,
                reason=payload.reason,
            )
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return self._map_material_read(material)

    async def delete_manual_consumption(self, movement_id: str) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.delete_manual_consumption(movement_id)
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return self._map_material_read(material)

    @staticmethod
    def _map_material_detail(material: Material) -> MaterialDetailRead:
        movements = [
            StockMovementRead(
                id=movement.id,
                created_at=movement.created_at,
                updated_at=movement.updated_at,
                movement_type=movement.movement_type,
                quantity_delta=movement.quantity_delta,
                unit_cost=movement.unit_cost,
                total_cost=movement.total_cost,
                balance_after=movement.balance_after,
                receipt_id=movement.receipt_id,
                receipt_number=movement.receipt.receipt_number if movement.receipt else None,
                work_id=movement.work_id,
                work_order_number=movement.work.order_number if movement.work else None,
                inventory_adjustment_id=movement.inventory_adjustment_id,
                inventory_adjustment_number=(
                    movement.inventory_adjustment.adjustment_number if movement.inventory_adjustment else None
                ),
                comment=movement.comment,
            )
            for movement in material.stock_movements[:20]
        ]
        payload = MaterialService._map_material_read(material).model_dump()
        return MaterialDetailRead(
            **payload,
            stock_value=(material.stock * material.average_price).quantize(Decimal("0.01")),
            movements=movements,
        )

    @staticmethod
    def _map_material_read(material: Material) -> MaterialRead:
        return MaterialRead(
            id=material.id,
            created_at=material.created_at,
            updated_at=material.updated_at,
            name=material.name,
            category=material.category,
            unit=material.unit,
            stock=material.stock,
            reserved_stock=material.reserved_stock,
            available_stock=(material.stock - material.reserved_stock).quantize(Decimal("0.001")),
            purchase_price=material.purchase_price,
            average_price=material.average_price,
            supplier=material.supplier,
            min_stock=material.min_stock,
            comment=material.comment,
            is_low_stock=material.stock <= material.min_stock,
        )

    async def _index_material(self, material: Material) -> None:
        await self._search.index_document(
            settings.elasticsearch_materials_index,
            material.id,
            build_material_search_document(material),
        )
