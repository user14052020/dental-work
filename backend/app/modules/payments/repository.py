from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.client import Client
from app.db.models.narad import Narad
from app.db.models.payment import Payment, PaymentAllocation
from app.db.models.work import Work


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.flush()
        return payment

    async def flush(self) -> None:
        await self.session.flush()

    async def get(self, payment_id: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment)
            .options(
                selectinload(Payment.client),
                selectinload(Payment.allocations)
                .selectinload(PaymentAllocation.work)
                .selectinload(Work.narad)
                .selectinload(Narad.works),
            )
            .where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, payment_number: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.payment_number == payment_number)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        client_id: str | None = None,
        method: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Payment], int]:
        stmt: Select = (
            select(Payment)
            .join(Client, Client.id == Payment.client_id)
            .outerjoin(PaymentAllocation, PaymentAllocation.payment_id == Payment.id)
            .outerjoin(Work, Work.id == PaymentAllocation.work_id)
            .outerjoin(Narad, Narad.id == Work.narad_id)
            .options(
                selectinload(Payment.client),
                selectinload(Payment.allocations)
                .selectinload(PaymentAllocation.work)
                .selectinload(Work.narad)
                .selectinload(Narad.works),
            )
            .distinct()
            .order_by(Payment.payment_date.desc(), Payment.created_at.desc())
        )
        count_stmt = (
            select(func.count(sa.distinct(Payment.id)))
            .select_from(Payment)
            .join(Client, Client.id == Payment.client_id)
            .outerjoin(PaymentAllocation, PaymentAllocation.payment_id == Payment.id)
            .outerjoin(Work, Work.id == PaymentAllocation.work_id)
            .outerjoin(Narad, Narad.id == Work.narad_id)
        )

        filters = []
        if search:
            filters.append(
                or_(
                    Payment.payment_number.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                    Payment.external_reference.ilike(f"%{search}%"),
                    Payment.comment.ilike(f"%{search}%"),
                    Work.order_number.ilike(f"%{search}%"),
                    Work.work_type.ilike(f"%{search}%"),
                    Narad.patient_name.ilike(f"%{search}%"),
                )
            )
        if client_id:
            filters.append(Payment.client_id == client_id)
        if method:
            filters.append(Payment.method == method)
        if date_from:
            filters.append(Payment.payment_date >= date_from)
        if date_to:
            filters.append(Payment.payment_date <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_by_client(self, client_id: str, *, limit: int = 10) -> list[Payment]:
        result = await self.session.execute(
            select(Payment)
            .options(
                selectinload(Payment.client),
                selectinload(Payment.allocations)
                .selectinload(PaymentAllocation.work)
                .selectinload(Work.narad)
                .selectinload(Narad.works),
            )
            .where(Payment.client_id == client_id)
            .order_by(Payment.payment_date.desc(), Payment.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_narad(self, narad_id: str, *, limit: int = 20) -> list[Payment]:
        result = await self.session.execute(
            select(Payment)
            .join(PaymentAllocation, PaymentAllocation.payment_id == Payment.id)
            .join(Work, Work.id == PaymentAllocation.work_id)
            .join(Narad, Narad.id == Work.narad_id)
            .options(
                selectinload(Payment.client),
                selectinload(Payment.allocations)
                .selectinload(PaymentAllocation.work)
                .selectinload(Work.narad)
                .selectinload(Narad.works),
            )
            .where(Narad.id == narad_id)
            .order_by(Payment.payment_date.desc(), Payment.created_at.desc())
            .distinct()
            .limit(limit)
        )
        return list(result.scalars().all())

    async def sum_allocations_by_work_ids(self, work_ids: list[str]) -> dict[str, Decimal]:
        if not work_ids:
            return {}

        result = await self.session.execute(
            select(
                PaymentAllocation.work_id,
                func.coalesce(func.sum(PaymentAllocation.amount), Decimal("0.00")),
            )
            .where(PaymentAllocation.work_id.in_(work_ids))
            .group_by(PaymentAllocation.work_id)
        )
        return {work_id: total for work_id, total in result.all()}

    async def sum_allocated_to_work(
        self,
        work_id: str,
        *,
        exclude_payment_id: str | None = None,
    ) -> Decimal:
        stmt = select(func.coalesce(func.sum(PaymentAllocation.amount), Decimal("0.00"))).where(
            PaymentAllocation.work_id == work_id
        )
        if exclude_payment_id:
            stmt = stmt.where(PaymentAllocation.payment_id != exclude_payment_id)
        total = await self.session.scalar(stmt)
        return Decimal(total or Decimal("0.00"))

    async def delete(self, payment: Payment) -> None:
        await self.session.delete(payment)
