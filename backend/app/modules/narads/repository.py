from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Select, and_, asc, desc, func, nulls_last, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.client import Client
from app.db.models.contractor import Contractor
from app.db.models.doctor import Doctor
from app.db.models.narad import Narad, NaradStatusLog
from app.db.models.work import Work, WorkItem, WorkMaterial


class NaradRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, narad: Narad) -> Narad:
        self.session.add(narad)
        await self.session.flush()
        return narad

    async def add_status_log(self, log: NaradStatusLog) -> NaradStatusLog:
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_by_number(self, narad_number: str) -> Narad | None:
        result = await self.session.execute(select(Narad).where(Narad.narad_number == narad_number))
        return result.scalar_one_or_none()

    async def get(self, narad_id: str) -> Narad | None:
        result = await self.session.execute(
            select(Narad)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.status_logs),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
                selectinload(Narad.works).selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
                selectinload(Narad.works).selectinload(Work.materials).selectinload(WorkMaterial.material),
            )
            .where(Narad.id == narad_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        client_id: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[Narad], int]:
        now = datetime.now(timezone.utc)
        terminal_statuses = ["completed", "delivered", "cancelled"]
        stmt: Select = (
            select(Narad)
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .outerjoin(Contractor, Contractor.id == Narad.contractor_id)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
                selectinload(Narad.works).selectinload(Work.materials).selectinload(WorkMaterial.material),
            )
            .order_by(Narad.received_at.desc(), Narad.created_at.desc())
        )
        count_stmt = (
            select(func.count(Narad.id))
            .select_from(Narad)
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .outerjoin(Contractor, Contractor.id == Narad.contractor_id)
        )

        filters = []
        if search:
            filters.append(
                or_(
                    Narad.narad_number.ilike(f"%{search}%"),
                    Narad.title.ilike(f"%{search}%"),
                    Narad.description.ilike(f"%{search}%"),
                    Narad.doctor_name.ilike(f"%{search}%"),
                    Narad.doctor_phone.ilike(f"%{search}%"),
                    Narad.patient_name.ilike(f"%{search}%"),
                    Narad.face_shape.ilike(f"%{search}%"),
                    Narad.implant_system.ilike(f"%{search}%"),
                    Narad.metal_type.ilike(f"%{search}%"),
                    Narad.shade_color.ilike(f"%{search}%"),
                    Narad.tooth_formula.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                    Client.contact_person.ilike(f"%{search}%"),
                    Contractor.name.ilike(f"%{search}%"),
                    Doctor.full_name.ilike(f"%{search}%"),
                )
            )
        if status:
            if status == "overdue":
                filters.append(Narad.deadline_at.is_not(None))
                filters.append(Narad.deadline_at < now)
                filters.append(~Narad.status.in_(terminal_statuses))
            else:
                filters.append(Narad.status == status)
        if client_id:
            filters.append(Narad.client_id == client_id)
        if date_from:
            filters.append(Narad.received_at >= date_from)
        if date_to:
            filters.append(Narad.received_at <= date_to)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_for_delivery(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        executor_id: str | None,
        sent: bool | None,
        ids: list[str] | None = None,
        sort_by: str = "deadline_at",
        sort_direction: str = "asc",
    ) -> tuple[list[Narad], int]:
        delivery_pending_count = (
            select(func.count(Work.id))
            .where(Work.narad_id == Narad.id, Work.delivery_sent.is_(False))
            .correlate(Narad)
            .scalar_subquery()
        )

        stmt: Select = (
            select(Narad, delivery_pending_count.label("delivery_pending_count"))
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
                selectinload(Narad.works).selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
            )
            .where(Narad.status.in_(["completed", "delivered"]))
            .where(Narad.works.any())
        )
        count_stmt = (
            select(func.count(Narad.id))
            .select_from(Narad)
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .outerjoin(Contractor, Contractor.id == Narad.contractor_id)
            .where(Narad.status.in_(["completed", "delivered"]))
            .where(Narad.works.any())
        )

        filters = []
        if search:
            filters.append(
                or_(
                    Narad.narad_number.ilike(f"%{search}%"),
                    Narad.title.ilike(f"%{search}%"),
                    Narad.description.ilike(f"%{search}%"),
                    Narad.doctor_name.ilike(f"%{search}%"),
                    Narad.patient_name.ilike(f"%{search}%"),
                    Narad.face_shape.ilike(f"%{search}%"),
                    Narad.implant_system.ilike(f"%{search}%"),
                    Narad.metal_type.ilike(f"%{search}%"),
                    Narad.shade_color.ilike(f"%{search}%"),
                    Narad.tooth_formula.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                    Client.contact_person.ilike(f"%{search}%"),
                    Client.delivery_address.ilike(f"%{search}%"),
                    Client.delivery_contact.ilike(f"%{search}%"),
                    Client.delivery_phone.ilike(f"%{search}%"),
                    Narad.works.any(Work.order_number.ilike(f"%{search}%")),
                    Narad.works.any(Work.work_type.ilike(f"%{search}%")),
                )
            )
        if client_id:
            filters.append(Narad.client_id == client_id)
        if executor_id:
            filters.append(Narad.works.any(Work.executor_id == executor_id))
        if sent is True:
            filters.append(delivery_pending_count == 0)
        elif sent is False:
            filters.append(delivery_pending_count > 0)
        if ids:
            filters.append(Narad.id.in_(ids))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        sort_fn = asc if sort_direction == "asc" else desc
        deadline_order = nulls_last(sort_fn(Narad.deadline_at))
        if sort_by == "client_name":
            stmt = stmt.order_by(sort_fn(Client.name), deadline_order, desc(Narad.received_at))
        elif sort_by == "received_at":
            stmt = stmt.order_by(sort_fn(Narad.received_at), asc(Client.name), deadline_order)
        else:
            stmt = stmt.order_by(deadline_order, asc(Client.name), desc(Narad.received_at))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.unique().scalars().all()), int(total_items or 0)

    async def list_for_delivery_by_ids(self, narad_ids: list[str]) -> list[Narad]:
        if not narad_ids:
            return []

        result = await self.session.execute(
            select(Narad)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
                selectinload(Narad.works).selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
            )
            .where(Narad.id.in_(narad_ids))
        )
        narads = {narad.id: narad for narad in result.scalars().all()}
        return [narads[narad_id] for narad_id in narad_ids if narad_id in narads]

    async def list_outside_works(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        state: str | None,
    ) -> tuple[list[Narad], int]:
        stmt: Select = (
            select(Narad)
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .outerjoin(Contractor, Contractor.id == Narad.contractor_id)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
            )
            .where(Narad.is_outside_work.is_(True))
        )
        count_stmt = (
            select(func.count(Narad.id))
            .select_from(Narad)
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Doctor, Doctor.id == Narad.doctor_id)
            .outerjoin(Contractor, Contractor.id == Narad.contractor_id)
            .where(Narad.is_outside_work.is_(True))
        )

        filters = []
        if search:
            filters.append(
                or_(
                    Narad.narad_number.ilike(f"%{search}%"),
                    Narad.title.ilike(f"%{search}%"),
                    Narad.description.ilike(f"%{search}%"),
                    Narad.patient_name.ilike(f"%{search}%"),
                    Narad.doctor_name.ilike(f"%{search}%"),
                    Narad.outside_lab_name.ilike(f"%{search}%"),
                    Contractor.name.ilike(f"%{search}%"),
                    Narad.outside_order_number.ilike(f"%{search}%"),
                    Narad.outside_comment.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                    Narad.works.any(Work.order_number.ilike(f"%{search}%")),
                    Narad.works.any(Work.work_type.ilike(f"%{search}%")),
                )
            )
        if client_id:
            filters.append(Narad.client_id == client_id)
        if state == "sent":
            filters.append(Narad.outside_sent_at.is_not(None))
            filters.append(Narad.outside_returned_at.is_(None))
        elif state == "returned":
            filters.append(Narad.outside_returned_at.is_not(None))
        elif state == "overdue":
            filters.append(Narad.outside_due_at.is_not(None))
            filters.append(Narad.outside_due_at < datetime.now(timezone.utc))
            filters.append(Narad.outside_returned_at.is_(None))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(
            nulls_last(asc(Narad.outside_due_at)),
            nulls_last(desc(Narad.outside_sent_at)),
            desc(Narad.received_at),
        )

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.unique().scalars().all()), int(total_items or 0)

    async def list_closed_by_client(
        self,
        client_id: str,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Narad]:
        stmt = (
            select(Narad)
            .options(
                selectinload(Narad.client),
                selectinload(Narad.doctor),
                selectinload(Narad.contractor),
                selectinload(Narad.works).selectinload(Work.executor),
                selectinload(Narad.works).selectinload(Work.catalog_item),
                selectinload(Narad.works).selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
            )
            .where(
                Narad.client_id == client_id,
                Narad.closed_at.is_not(None),
                Narad.works.any(),
            )
            .order_by(Narad.closed_at.asc(), Narad.received_at.asc(), Narad.narad_number.asc())
        )

        if date_from is not None:
            stmt = stmt.where(Narad.closed_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Narad.closed_at <= date_to)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
