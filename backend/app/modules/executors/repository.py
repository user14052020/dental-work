from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.executor import Executor
from app.db.models.operation import ExecutorCategory
from app.db.models.work import Work


class ExecutorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, executor: Executor) -> Executor:
        self.session.add(executor)
        await self.session.flush()
        return executor

    async def get(self, executor_id: str) -> Executor | None:
        result = await self.session.execute(
            select(Executor)
            .options(selectinload(Executor.payment_category))
            .where(Executor.id == executor_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
        ids: list[str] | None = None,
    ) -> tuple[list[tuple[Executor, int, Decimal, Decimal, Decimal]], int]:
        stmt: Select = (
            select(
                Executor,
                func.count(Work.id),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")),
                func.coalesce(func.sum(Work.labor_cost), Decimal("0.00")),
                func.coalesce(
                    func.sum(
                        case(
                            (func.date_trunc("month", Work.closed_at) == func.date_trunc("month", func.now()), Work.labor_cost),
                            else_=Decimal("0.00"),
                        )
                    ),
                    Decimal("0.00"),
                ),
            )
            .options(selectinload(Executor.payment_category))
            .outerjoin(Work, Work.executor_id == Executor.id)
            .outerjoin(ExecutorCategory, Executor.payment_category_id == ExecutorCategory.id)
            .group_by(Executor.id)
            .order_by(Executor.created_at.desc())
        )
        count_stmt = select(func.count(Executor.id)).outerjoin(
            ExecutorCategory,
            Executor.payment_category_id == ExecutorCategory.id,
        )

        if search:
            filter_expression = or_(
                Executor.full_name.ilike(f"%{search}%"),
                Executor.phone.ilike(f"%{search}%"),
                Executor.email.ilike(f"%{search}%"),
                Executor.specialization.ilike(f"%{search}%"),
                Executor.comment.ilike(f"%{search}%"),
                ExecutorCategory.code.ilike(f"%{search}%"),
                ExecutorCategory.name.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if active_only is not None:
            stmt = stmt.where(Executor.is_active == active_only)
            count_stmt = count_stmt.where(Executor.is_active == active_only)

        if ids:
            stmt = stmt.where(Executor.id.in_(ids))
            count_stmt = count_stmt.where(Executor.id.in_(ids))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.all()), int(total_items or 0)

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Executor]:
        result = await self.session.execute(
            select(Executor)
            .options(selectinload(Executor.payment_category))
            .order_by(Executor.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
