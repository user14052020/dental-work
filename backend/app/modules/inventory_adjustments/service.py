from __future__ import annotations

from decimal import Decimal

from app.common.enums import StockMovementType
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_material_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.inventory_adjustment import InventoryAdjustment, InventoryAdjustmentItem
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.inventory_adjustments.schemas import (
    InventoryAdjustmentCompactRead,
    InventoryAdjustmentCreate,
    InventoryAdjustmentItemRead,
    InventoryAdjustmentListResponse,
    InventoryAdjustmentRead,
)


THREE_PLACES = Decimal("0.001")
TWO_PLACES = Decimal("0.01")


class InventoryAdjustmentService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService, search: SearchService):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_adjustments(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        date_from,
        date_to,
    ) -> InventoryAdjustmentListResponse:
        async with self._uow as uow:
            adjustments, total_items = await uow.inventory_adjustments.list(
                page=page,
                page_size=page_size,
                search=search,
                date_from=date_from,
                date_to=date_to,
            )
            items = [self._map_adjustment_compact(adjustment) for adjustment in adjustments]
        return PaginatedResponse[InventoryAdjustmentCompactRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_adjustment(self, adjustment_id: str) -> InventoryAdjustmentRead:
        async with self._uow as uow:
            adjustment = await uow.inventory_adjustments.get(adjustment_id)
            if adjustment is None:
                raise NotFoundError("inventory_adjustment", adjustment_id)
            return self._map_adjustment_detail(adjustment)

    async def create_adjustment(self, payload: InventoryAdjustmentCreate) -> InventoryAdjustmentRead:
        async with self._uow as uow:
            existing = await uow.inventory_adjustments.get_by_number(payload.adjustment_number)
            if existing is not None:
                raise ConflictError("Adjustment number already exists.", code="inventory_adjustment_number_exists")

            material_ids = [item.material_id for item in payload.items]
            if len(set(material_ids)) != len(material_ids):
                raise ConflictError(
                    "Duplicate materials are not allowed in one inventory document.",
                    code="duplicate_material_in_inventory_adjustment",
                )
            materials = {material.id: material for material in await uow.materials.list_by_ids(material_ids)}

            adjustment = await uow.inventory_adjustments.add(
                InventoryAdjustment(
                    adjustment_number=payload.adjustment_number,
                    recorded_at=payload.recorded_at,
                    comment=payload.comment,
                )
            )

            touched_materials = []
            for index, item in enumerate(payload.items):
                material = materials.get(item.material_id)
                if material is None:
                    raise NotFoundError("material", item.material_id)

                expected_stock = material.stock.quantize(THREE_PLACES)
                actual_stock = item.actual_stock.quantize(THREE_PLACES)
                if actual_stock < material.reserved_stock:
                    raise ConflictError(
                        "Actual stock cannot be lower than reserved stock.",
                        code="inventory_below_reserved_stock",
                        details={
                            "material_id": material.id,
                            "actual_stock": str(actual_stock),
                            "reserved_stock": str(material.reserved_stock),
                        },
                    )
                quantity_delta = (actual_stock - expected_stock).quantize(THREE_PLACES)
                unit_cost = material.average_price.quantize(TWO_PLACES)
                total_cost = (unit_cost * abs(quantity_delta)).quantize(TWO_PLACES)

                adjustment_item = await uow.inventory_adjustments.add_item(
                    InventoryAdjustmentItem(
                        adjustment_id=adjustment.id,
                        material_id=material.id,
                        expected_stock=expected_stock,
                        actual_stock=actual_stock,
                        quantity_delta=quantity_delta,
                        unit_cost=unit_cost,
                        total_cost=total_cost,
                        sort_order=index,
                        comment=item.comment,
                    )
                )
                adjustment_item.material = material

                if quantity_delta != Decimal("0.000"):
                    await uow.materials.change_stock(
                        material.id,
                        quantity_delta=quantity_delta,
                        movement_type=StockMovementType.INVENTORY.value,
                        unit_cost=unit_cost,
                        comment=item.comment or f"Инвентаризация {adjustment.adjustment_number}",
                        inventory_adjustment_id=adjustment.id,
                        respect_reservations=False,
                    )
                touched_materials.append(material)

            await uow.commit()

        for material in touched_materials:
            await self._search.index_document(
                settings.elasticsearch_materials_index,
                material.id,
                build_material_search_document(material),
            )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_adjustment(adjustment.id)

    @staticmethod
    def _map_adjustment_compact(adjustment: InventoryAdjustment) -> InventoryAdjustmentCompactRead:
        changed_items = [item for item in adjustment.items if item.quantity_delta != Decimal("0.000")]
        positive_delta_total = sum(
            (item.quantity_delta for item in changed_items if item.quantity_delta > 0),
            Decimal("0.000"),
        ).quantize(THREE_PLACES)
        negative_delta_total = sum(
            (abs(item.quantity_delta) for item in changed_items if item.quantity_delta < 0),
            Decimal("0.000"),
        ).quantize(THREE_PLACES)
        total_cost_impact = sum((item.total_cost for item in changed_items), Decimal("0.00")).quantize(TWO_PLACES)
        return InventoryAdjustmentCompactRead(
            id=adjustment.id,
            created_at=adjustment.created_at,
            updated_at=adjustment.updated_at,
            adjustment_number=adjustment.adjustment_number,
            recorded_at=adjustment.recorded_at,
            items_count=len(adjustment.items),
            changed_items_count=len(changed_items),
            positive_delta_total=positive_delta_total,
            negative_delta_total=negative_delta_total,
            total_cost_impact=total_cost_impact,
        )

    def _map_adjustment_detail(self, adjustment: InventoryAdjustment) -> InventoryAdjustmentRead:
        compact = self._map_adjustment_compact(adjustment)
        items = [
            InventoryAdjustmentItemRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                material_id=item.material_id,
                material_name=item.material.name,
                unit=item.material.unit,
                expected_stock=item.expected_stock,
                actual_stock=item.actual_stock,
                quantity_delta=item.quantity_delta,
                unit_cost=item.unit_cost,
                total_cost=item.total_cost,
                sort_order=item.sort_order,
                comment=item.comment,
            )
            for item in sorted(adjustment.items, key=lambda row: row.sort_order)
        ]
        return InventoryAdjustmentRead(**compact.model_dump(), comment=adjustment.comment, items=items)
