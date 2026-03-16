from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.enums import WorkStatus
from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.work import Work, WorkMaterial


class WorkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, work: Work) -> Work:
        self.session.add(work)
        await self.session.flush()
        return work

    async def add_material_usage(self, work_material: WorkMaterial) -> WorkMaterial:
        self.session.add(work_material)
        await self.session.flush()
        return work_material

    async def get(self, work_id: str) -> Work | None:
        result = await self.session.execute(
            select(Work)
            .options(
                selectinload(Work.client),
                selectinload(Work.executor),
                selectinload(Work.materials).selectinload(WorkMaterial.material),
            )
            .where(Work.id == work_id)
        )
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> Work | None:
        result = await self.session.execute(select(Work).where(Work.order_number == order_number))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        order_number: str | None,
        status: str | None,
        client_id: str | None,
        executor_id: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        ids: list[str] | None,
    ) -> tuple[list[Work], int]:
        stmt: Select = (
            select(Work)
            .options(selectinload(Work.client), selectinload(Work.executor))
            .order_by(Work.received_at.desc())
        )
        count_stmt = select(func.count(Work.id))

        filters = []
        if order_number:
            filters.append(
                (Work.order_number.ilike(f"%{order_number}%"))
                | (Work.work_type.ilike(f"%{order_number}%"))
                | (Work.description.ilike(f"%{order_number}%"))
                | (Work.comment.ilike(f"%{order_number}%"))
            )
        if status:
            filters.append(Work.status == status)
        if client_id:
            filters.append(Work.client_id == client_id)
        if executor_id:
            filters.append(Work.executor_id == executor_id)
        if date_from:
            filters.append(Work.received_at >= date_from)
        if date_to:
            filters.append(Work.received_at <= date_to)
        if ids:
            filters.append(Work.id.in_(ids))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_by_client(self, client_id: str) -> list[Work]:
        result = await self.session.execute(
            select(Work).options(selectinload(Work.client), selectinload(Work.executor)).where(Work.client_id == client_id)
        )
        return list(result.scalars().all())

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Work]:
        result = await self.session.execute(
            select(Work)
            .options(
                selectinload(Work.client),
                selectinload(Work.executor),
                selectinload(Work.materials).selectinload(WorkMaterial.material),
            )
            .order_by(Work.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
