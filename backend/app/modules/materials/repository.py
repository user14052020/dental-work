from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.enums import StockMovementType
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.material import Material
from app.db.models.material_receipt import StockMovement


class MaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, material: Material) -> Material:
        self.session.add(material)
        await self.session.flush()
        return material

    async def add_stock_movement(self, movement: StockMovement) -> StockMovement:
        self.session.add(movement)
        await self.session.flush()
        return movement

    async def get_stock_movement(self, movement_id: str) -> StockMovement | None:
        result = await self.session.execute(
            select(StockMovement)
            .options(selectinload(StockMovement.material))
            .where(StockMovement.id == movement_id)
        )
        return result.scalar_one_or_none()

    async def get(self, material_id: str) -> Material | None:
        result = await self.session.execute(
            select(Material)
            .options(
                selectinload(Material.stock_movements).selectinload(StockMovement.receipt),
                selectinload(Material.stock_movements).selectinload(StockMovement.work),
                selectinload(Material.stock_movements).selectinload(StockMovement.inventory_adjustment),
            )
            .where(Material.id == material_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        low_stock_only: bool,
        ids: list[str] | None = None,
    ) -> tuple[list[Material], int]:
        stmt: Select = select(Material).order_by(Material.created_at.desc())
        count_stmt = select(func.count(Material.id))

        if search:
            filter_expression = or_(
                Material.name.ilike(f"%{search}%"),
                Material.category.ilike(f"%{search}%"),
                Material.unit.ilike(f"%{search}%"),
                Material.supplier.ilike(f"%{search}%"),
                Material.comment.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if low_stock_only:
            low_stock_filter = Material.stock <= Material.min_stock
            stmt = stmt.where(low_stock_filter)
            count_stmt = count_stmt.where(low_stock_filter)

        if ids:
            stmt = stmt.where(Material.id.in_(ids))
            count_stmt = count_stmt.where(Material.id.in_(ids))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_by_ids(self, ids: list[str]) -> list[Material]:
        if not ids:
            return []
        result = await self.session.execute(select(Material).where(Material.id.in_(ids)))
        return list(result.scalars().all())

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Material]:
        result = await self.session.execute(
            select(Material).order_by(Material.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def consume_stock(self, material_id: str, quantity: Decimal) -> Material:
        return await self.change_stock(
            material_id,
            quantity_delta=-quantity,
            movement_type=StockMovementType.CONSUME.value,
            unit_cost=None,
            comment="Списание материала",
        )

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
        material = await self.get(material_id)
        if material is None:
            raise NotFoundError("material", material_id)
        available_stock = (material.stock - material.reserved_stock).quantize(Decimal("0.001"))
        if quantity_delta < 0 and (
            (available_stock if respect_reservations else material.stock) < abs(quantity_delta)
        ):
            raise ConflictError(
                "Material stock is insufficient for this operation.",
                code="insufficient_material_stock",
                details={
                    "material_id": material_id,
                    "requested": str(abs(quantity_delta)),
                    "available": str(available_stock if respect_reservations else material.stock),
                },
            )
        next_balance = (material.stock + quantity_delta).quantize(Decimal("0.001"))
        material.stock = next_balance
        resolved_unit_cost = (unit_cost if unit_cost is not None else material.average_price).quantize(Decimal("0.01"))
        total_cost = (resolved_unit_cost * abs(quantity_delta)).quantize(Decimal("0.01"))
        await self.add_stock_movement(
            StockMovement(
                material_id=material.id,
                movement_type=movement_type,
                quantity_delta=quantity_delta,
                unit_cost=resolved_unit_cost,
                total_cost=total_cost,
                balance_after=next_balance,
                receipt_id=receipt_id,
                work_id=work_id,
                inventory_adjustment_id=inventory_adjustment_id,
                comment=comment,
            )
        )
        await self.session.flush()
        return material

    async def change_reserved_stock(
        self,
        material_id: str,
        *,
        quantity_delta: Decimal,
        movement_type: str,
        comment: str | None = None,
        work_id: str | None = None,
    ) -> Material:
        material = await self.get(material_id)
        if material is None:
            raise NotFoundError("material", material_id)

        available_stock = (material.stock - material.reserved_stock).quantize(Decimal("0.001"))
        if quantity_delta > 0 and available_stock < quantity_delta:
            raise ConflictError(
                "Material stock is insufficient for reservation.",
                code="insufficient_material_stock",
                details={
                    "material_id": material_id,
                    "requested": str(quantity_delta),
                    "available": str(available_stock),
                },
            )
        if quantity_delta < 0 and material.reserved_stock < abs(quantity_delta):
            raise ConflictError(
                "Reserved stock is insufficient for this operation.",
                code="insufficient_reserved_stock",
                details={
                    "material_id": material_id,
                    "requested": str(abs(quantity_delta)),
                    "reserved": str(material.reserved_stock),
                },
            )

        material.reserved_stock = (material.reserved_stock + quantity_delta).quantize(Decimal("0.001"))
        resolved_unit_cost = material.average_price.quantize(Decimal("0.01"))
        total_cost = (resolved_unit_cost * abs(quantity_delta)).quantize(Decimal("0.01"))
        await self.add_stock_movement(
            StockMovement(
                material_id=material.id,
                movement_type=movement_type,
                quantity_delta=quantity_delta,
                unit_cost=resolved_unit_cost,
                total_cost=total_cost,
                balance_after=material.stock,
                work_id=work_id,
                comment=comment,
            )
        )
        await self.session.flush()
        return material

    async def update_manual_consumption(
        self,
        movement_id: str,
        *,
        quantity: Decimal,
        reason: str | None = None,
    ) -> Material:
        movement = await self.get_stock_movement(movement_id)
        if movement is None:
            raise NotFoundError("stock_movement", movement_id)
        if (
            movement.movement_type != StockMovementType.CONSUME.value
            or movement.work_id is not None
            or movement.receipt_id is not None
        ):
            raise ConflictError(
                "Only manual actual consumption entries can be updated.",
                code="invalid_stock_movement_edit",
            )

        movement.quantity_delta = (-quantity).quantize(Decimal("0.001"))
        movement.total_cost = (movement.unit_cost * quantity).quantize(Decimal("0.01"))
        movement.comment = reason
        await self._recalculate_material_stock(movement.material_id)
        material = await self.get(movement.material_id)
        if material is None:
            raise NotFoundError("material", movement.material_id)
        return material

    async def delete_manual_consumption(self, movement_id: str) -> Material:
        movement = await self.get_stock_movement(movement_id)
        if movement is None:
            raise NotFoundError("stock_movement", movement_id)
        if (
            movement.movement_type != StockMovementType.CONSUME.value
            or movement.work_id is not None
            or movement.receipt_id is not None
        ):
            raise ConflictError(
                "Only manual actual consumption entries can be deleted.",
                code="invalid_stock_movement_delete",
            )

        material_id = movement.material_id
        await self.session.delete(movement)
        await self.session.flush()
        await self._recalculate_material_stock(material_id)
        material = await self.get(material_id)
        if material is None:
            raise NotFoundError("material", material_id)
        return material

    async def _recalculate_material_stock(self, material_id: str) -> None:
        material = await self.get(material_id)
        if material is None:
            raise NotFoundError("material", material_id)

        result = await self.session.execute(
            select(StockMovement)
            .where(StockMovement.material_id == material_id)
            .order_by(StockMovement.created_at.asc(), StockMovement.id.asc())
        )
        movements = list(result.scalars().all())

        current_stock = Decimal("0.000")
        stock_affecting_types = {
            StockMovementType.OPENING_BALANCE.value,
            StockMovementType.RECEIPT.value,
            StockMovementType.CONSUME.value,
            StockMovementType.RESTORE.value,
            StockMovementType.ADJUSTMENT.value,
            StockMovementType.INVENTORY.value,
        }

        for movement in movements:
            if movement.movement_type in stock_affecting_types:
                current_stock = (current_stock + movement.quantity_delta).quantize(Decimal("0.001"))
                if current_stock < Decimal("0.000"):
                    raise ConflictError(
                        "Material stock is insufficient for this operation.",
                        code="insufficient_material_stock",
                        details={"material_id": material_id},
                    )
            movement.balance_after = current_stock

        if current_stock < material.reserved_stock:
            raise ConflictError(
                "Material stock is insufficient after recalculation.",
                code="insufficient_material_stock",
                details={
                    "material_id": material_id,
                    "stock": str(current_stock),
                    "reserved": str(material.reserved_stock),
                },
            )

        material.stock = current_stock
        await self.session.flush()
