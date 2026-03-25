from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.material_receipt import MaterialReceipt, MaterialReceiptItem


class MaterialReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, receipt: MaterialReceipt) -> MaterialReceipt:
        self.session.add(receipt)
        await self.session.flush()
        return receipt

    async def add_item(self, item: MaterialReceiptItem) -> MaterialReceiptItem:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get(self, receipt_id: str) -> MaterialReceipt | None:
        result = await self.session.execute(
            select(MaterialReceipt)
            .options(selectinload(MaterialReceipt.items).selectinload(MaterialReceiptItem.material))
            .where(MaterialReceipt.id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, receipt_number: str) -> MaterialReceipt | None:
        result = await self.session.execute(
            select(MaterialReceipt).where(MaterialReceipt.receipt_number == receipt_number)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        supplier: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[MaterialReceipt], int]:
        stmt: Select = (
            select(MaterialReceipt)
            .options(selectinload(MaterialReceipt.items))
            .order_by(MaterialReceipt.received_at.desc(), MaterialReceipt.created_at.desc())
        )
        count_stmt = select(func.count(MaterialReceipt.id))

        filters = []
        if search:
            filters.append(
                or_(
                    MaterialReceipt.receipt_number.ilike(f"%{search}%"),
                    MaterialReceipt.supplier.ilike(f"%{search}%"),
                    MaterialReceipt.comment.ilike(f"%{search}%"),
                )
            )
        if supplier:
            filters.append(MaterialReceipt.supplier.ilike(f"%{supplier}%"))
        if date_from:
            filters.append(MaterialReceipt.received_at >= date_from)
        if date_to:
            filters.append(MaterialReceipt.received_at <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)
