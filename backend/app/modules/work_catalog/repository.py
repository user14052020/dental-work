from __future__ import annotations

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.work_catalog import WorkCatalogItem, WorkCatalogItemOperation


class WorkCatalogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, item: WorkCatalogItem) -> WorkCatalogItem:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get(self, item_id: str) -> WorkCatalogItem | None:
        result = await self.session.execute(
            select(WorkCatalogItem)
            .options(selectinload(WorkCatalogItem.default_operations).selectinload(WorkCatalogItemOperation.operation))
            .where(WorkCatalogItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> WorkCatalogItem | None:
        result = await self.session.execute(
            select(WorkCatalogItem)
            .options(selectinload(WorkCatalogItem.default_operations).selectinload(WorkCatalogItemOperation.operation))
            .where(WorkCatalogItem.code == code)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
        category: str | None = None,
        ids: list[str] | None = None,
    ) -> tuple[list[WorkCatalogItem], int]:
        stmt: Select = (
            select(WorkCatalogItem)
            .options(selectinload(WorkCatalogItem.default_operations).selectinload(WorkCatalogItemOperation.operation))
            .order_by(WorkCatalogItem.sort_order.asc(), WorkCatalogItem.name.asc())
        )
        count_stmt = select(func.count(WorkCatalogItem.id))
        filters = []
        if search:
            filters.append(
                or_(
                    WorkCatalogItem.code.ilike(f"%{search}%"),
                    WorkCatalogItem.name.ilike(f"%{search}%"),
                    WorkCatalogItem.category.ilike(f"%{search}%"),
                    WorkCatalogItem.description.ilike(f"%{search}%"),
                )
            )
        if active_only is not None:
            filters.append(WorkCatalogItem.is_active.is_(active_only))
        if category:
            filters.append(WorkCatalogItem.category.ilike(f"%{category}%"))
        if ids:
            filters.append(WorkCatalogItem.id.in_(ids))
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[WorkCatalogItem]:
        result = await self.session.execute(
            select(WorkCatalogItem)
            .options(selectinload(WorkCatalogItem.default_operations).selectinload(WorkCatalogItemOperation.operation))
            .order_by(WorkCatalogItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_ids(self, item_ids: list[str]) -> list[WorkCatalogItem]:
        if not item_ids:
            return []
        result = await self.session.execute(
            select(WorkCatalogItem)
            .options(selectinload(WorkCatalogItem.default_operations).selectinload(WorkCatalogItemOperation.operation))
            .where(WorkCatalogItem.id.in_(item_ids))
        )
        return list(result.scalars().all())
