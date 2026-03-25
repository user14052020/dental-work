from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.inventory_adjustment import InventoryAdjustment, InventoryAdjustmentItem


class InventoryAdjustmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, adjustment: InventoryAdjustment) -> InventoryAdjustment:
        self.session.add(adjustment)
        await self.session.flush()
        return adjustment

    async def add_item(self, item: InventoryAdjustmentItem) -> InventoryAdjustmentItem:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get(self, adjustment_id: str) -> InventoryAdjustment | None:
        result = await self.session.execute(
            select(InventoryAdjustment)
            .options(selectinload(InventoryAdjustment.items).selectinload(InventoryAdjustmentItem.material))
            .where(InventoryAdjustment.id == adjustment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, adjustment_number: str) -> InventoryAdjustment | None:
        result = await self.session.execute(
            select(InventoryAdjustment).where(InventoryAdjustment.adjustment_number == adjustment_number)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[InventoryAdjustment], int]:
        stmt: Select = (
            select(InventoryAdjustment)
            .options(selectinload(InventoryAdjustment.items))
            .order_by(InventoryAdjustment.recorded_at.desc(), InventoryAdjustment.created_at.desc())
        )
        count_stmt = select(func.count(InventoryAdjustment.id))

        filters = []
        if search:
            filters.append(
                or_(
                    InventoryAdjustment.adjustment_number.ilike(f"%{search}%"),
                    InventoryAdjustment.comment.ilike(f"%{search}%"),
                )
            )
        if date_from:
            filters.append(InventoryAdjustment.recorded_at >= date_from)
        if date_to:
            filters.append(InventoryAdjustment.recorded_at <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)
