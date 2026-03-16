from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.client import Client
from app.db.models.work import Work


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, client: Client) -> Client:
        self.session.add(client)
        await self.session.flush()
        return client

    async def get(self, client_id: str) -> Client | None:
        result = await self.session.execute(
            select(Client).options(selectinload(Client.works)).where(Client.id == client_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        ids: list[str] | None = None,
    ) -> tuple[list[tuple[Client, int, Decimal, Decimal]], int]:
        stmt: Select = (
            select(
                Client,
                func.count(Work.id),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")),
                func.coalesce(func.sum(Work.amount_paid), Decimal("0.00")),
            )
            .outerjoin(Work, Work.client_id == Client.id)
            .group_by(Client.id)
            .order_by(Client.created_at.desc())
        )
        count_stmt = select(func.count(Client.id))

        if search:
            filter_expression = or_(
                Client.name.ilike(f"%{search}%"),
                Client.contact_person.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%"),
                Client.address.ilike(f"%{search}%"),
                Client.comment.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if ids:
            stmt = stmt.where(Client.id.in_(ids))
            count_stmt = count_stmt.where(Client.id.in_(ids))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.all()), int(total_items or 0)

    async def delete(self, client: Client) -> None:
        await self.session.delete(client)

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Client]:
        result = await self.session.execute(
            select(Client).order_by(Client.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())
