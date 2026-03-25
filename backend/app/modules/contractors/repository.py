from __future__ import annotations

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contractor import Contractor


class ContractorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, contractor: Contractor) -> Contractor:
        self.session.add(contractor)
        await self.session.flush()
        return contractor

    async def get(self, contractor_id: str) -> Contractor | None:
        result = await self.session.execute(select(Contractor).where(Contractor.id == contractor_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active_only: bool | None = None,
    ) -> tuple[list[Contractor], int]:
        stmt: Select = select(Contractor).order_by(Contractor.name.asc())
        count_stmt = select(func.count(Contractor.id))

        filters = []
        if search:
            filters.append(
                or_(
                    Contractor.name.ilike(f"%{search}%"),
                    Contractor.contact_person.ilike(f"%{search}%"),
                    Contractor.phone.ilike(f"%{search}%"),
                    Contractor.email.ilike(f"%{search}%"),
                    Contractor.address.ilike(f"%{search}%"),
                    Contractor.comment.ilike(f"%{search}%"),
                )
            )
        if active_only is not None:
            filters.append(Contractor.is_active.is_(active_only))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)
