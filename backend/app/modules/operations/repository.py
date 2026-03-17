from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.operation import (
    ExecutorCategory,
    OperationCatalog,
    OperationCategoryRate,
    WorkOperation,
    WorkOperationLog,
)


class OperationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_category(self, category: ExecutorCategory) -> ExecutorCategory:
        self.session.add(category)
        await self.session.flush()
        return category

    async def get_category(self, category_id: str) -> ExecutorCategory | None:
        result = await self.session.execute(select(ExecutorCategory).where(ExecutorCategory.id == category_id))
        return result.scalar_one_or_none()

    async def get_category_by_code(self, code: str) -> ExecutorCategory | None:
        result = await self.session.execute(select(ExecutorCategory).where(ExecutorCategory.code == code))
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
    ) -> tuple[list[ExecutorCategory], int]:
        stmt: Select = select(ExecutorCategory).order_by(ExecutorCategory.sort_order.asc(), ExecutorCategory.created_at.asc())
        count_stmt = select(func.count(ExecutorCategory.id))

        if search:
            filter_expression = or_(
                ExecutorCategory.code.ilike(f"%{search}%"),
                ExecutorCategory.name.ilike(f"%{search}%"),
                ExecutorCategory.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if active_only is not None:
            stmt = stmt.where(ExecutorCategory.is_active == active_only)
            count_stmt = count_stmt.where(ExecutorCategory.is_active == active_only)

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_categories_by_ids(self, ids: list[str]) -> list[ExecutorCategory]:
        if not ids:
            return []
        result = await self.session.execute(select(ExecutorCategory).where(ExecutorCategory.id.in_(ids)))
        return list(result.scalars().all())

    async def add_operation(self, operation: OperationCatalog) -> OperationCatalog:
        self.session.add(operation)
        await self.session.flush()
        return operation

    async def get_operation(self, operation_id: str) -> OperationCatalog | None:
        result = await self.session.execute(
            select(OperationCatalog)
            .options(selectinload(OperationCatalog.payment_rates).selectinload(OperationCategoryRate.executor_category))
            .where(OperationCatalog.id == operation_id)
        )
        return result.scalar_one_or_none()

    async def get_operation_by_code(self, code: str) -> OperationCatalog | None:
        result = await self.session.execute(
            select(OperationCatalog)
            .options(selectinload(OperationCatalog.payment_rates).selectinload(OperationCategoryRate.executor_category))
            .where(OperationCatalog.code == code)
        )
        return result.scalar_one_or_none()

    async def list_operations(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
        ids: list[str] | None = None,
    ) -> tuple[list[OperationCatalog], int]:
        stmt: Select = (
            select(OperationCatalog)
            .options(selectinload(OperationCatalog.payment_rates).selectinload(OperationCategoryRate.executor_category))
            .order_by(OperationCatalog.sort_order.asc(), OperationCatalog.created_at.asc())
        )
        count_stmt = select(func.count(OperationCatalog.id))

        if search:
            filter_expression = or_(
                OperationCatalog.code.ilike(f"%{search}%"),
                OperationCatalog.name.ilike(f"%{search}%"),
                OperationCatalog.operation_group.ilike(f"%{search}%"),
                OperationCatalog.description.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if active_only is not None:
            stmt = stmt.where(OperationCatalog.is_active == active_only)
            count_stmt = count_stmt.where(OperationCatalog.is_active == active_only)

        if ids:
            stmt = stmt.where(OperationCatalog.id.in_(ids))
            count_stmt = count_stmt.where(OperationCatalog.id.in_(ids))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_operations_by_ids(self, ids: list[str]) -> list[OperationCatalog]:
        if not ids:
            return []
        result = await self.session.execute(
            select(OperationCatalog)
            .options(selectinload(OperationCatalog.payment_rates).selectinload(OperationCategoryRate.executor_category))
            .where(OperationCatalog.id.in_(ids))
        )
        return list(result.scalars().all())

    async def list_operations_for_indexing(self, *, offset: int, limit: int) -> list[OperationCatalog]:
        result = await self.session.execute(
            select(OperationCatalog)
            .options(selectinload(OperationCatalog.payment_rates).selectinload(OperationCategoryRate.executor_category))
            .order_by(OperationCatalog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_work_operation(self, work_operation: WorkOperation) -> WorkOperation:
        self.session.add(work_operation)
        await self.session.flush()
        return work_operation

    async def add_work_operation_log(self, log: WorkOperationLog) -> WorkOperationLog:
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_work_operation(self, work_id: str, work_operation_id: str) -> WorkOperation | None:
        result = await self.session.execute(
            select(WorkOperation)
            .options(
                selectinload(WorkOperation.executor),
                selectinload(WorkOperation.executor_category),
                selectinload(WorkOperation.logs),
            )
            .where(WorkOperation.id == work_operation_id, WorkOperation.work_id == work_id)
        )
        return result.scalar_one_or_none()
