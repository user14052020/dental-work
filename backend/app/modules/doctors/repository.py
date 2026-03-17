from __future__ import annotations

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.client import Client
from app.db.models.doctor import Doctor


class DoctorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, doctor: Doctor) -> Doctor:
        self.session.add(doctor)
        await self.session.flush()
        return doctor

    async def get(self, doctor_id: str) -> Doctor | None:
        result = await self.session.execute(
            select(Doctor).options(selectinload(Doctor.client)).where(Doctor.id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
        client_id: str | None = None,
        ids: list[str] | None = None,
    ) -> tuple[list[Doctor], int]:
        stmt: Select = select(Doctor).options(selectinload(Doctor.client)).order_by(Doctor.full_name.asc())
        count_stmt = select(func.count(Doctor.id))

        filters = []
        if search:
            filters.append(
                or_(
                    Doctor.full_name.ilike(f"%{search}%"),
                    Doctor.phone.ilike(f"%{search}%"),
                    Doctor.email.ilike(f"%{search}%"),
                    Doctor.specialization.ilike(f"%{search}%"),
                    Doctor.comment.ilike(f"%{search}%"),
                )
            )
        if active_only is not None:
            filters.append(Doctor.is_active.is_(active_only))
        if client_id:
            filters.append(Doctor.client_id == client_id)
        if ids:
            filters.append(Doctor.id.in_(ids))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_by_ids(self, ids: list[str]) -> list[Doctor]:
        if not ids:
            return []
        result = await self.session.execute(
            select(Doctor).options(selectinload(Doctor.client)).where(Doctor.id.in_(ids))
        )
        return list(result.scalars().all())

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Doctor]:
        result = await self.session.execute(
            select(Doctor)
            .options(selectinload(Doctor.client))
            .order_by(Doctor.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
