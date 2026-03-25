from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.enums import WorkStatus
from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.narad import Narad
from app.db.models.operation import WorkOperation
from app.db.models.payment import Payment, PaymentAllocation
from app.db.models.work import Work, WorkAttachment, WorkChangeLog, WorkItem, WorkMaterial
from app.db.models.work_catalog import WorkCatalogItem


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

    async def add_work_item(self, work_item: WorkItem) -> WorkItem:
        self.session.add(work_item)
        await self.session.flush()
        return work_item

    async def add_change_log(self, work_change_log: WorkChangeLog) -> WorkChangeLog:
        self.session.add(work_change_log)
        await self.session.flush()
        return work_change_log

    async def add_attachment(self, attachment: WorkAttachment) -> WorkAttachment:
        self.session.add(attachment)
        await self.session.flush()
        return attachment

    async def get_attachment(self, work_id: str, attachment_id: str) -> WorkAttachment | None:
        result = await self.session.execute(
            select(WorkAttachment).where(WorkAttachment.id == attachment_id, WorkAttachment.work_id == work_id)
        )
        return result.scalar_one_or_none()

    async def get(self, work_id: str) -> Work | None:
        result = await self.session.execute(
            select(Work)
            .options(
                selectinload(Work.client),
                selectinload(Work.narad),
                selectinload(Work.executor),
                selectinload(Work.catalog_item),
                selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
                selectinload(Work.materials).selectinload(WorkMaterial.material),
                selectinload(Work.work_operations).selectinload(WorkOperation.executor),
                selectinload(Work.work_operations).selectinload(WorkOperation.executor_category),
                selectinload(Work.work_operations).selectinload(WorkOperation.logs),
                selectinload(Work.attachments),
                selectinload(Work.payment_allocations)
                .selectinload(PaymentAllocation.payment)
                .selectinload(Payment.allocations),
                selectinload(Work.change_logs),
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
            .join(Narad, Narad.id == Work.narad_id)
            .outerjoin(WorkCatalogItem, WorkCatalogItem.id == Work.work_catalog_item_id)
            .options(
                selectinload(Work.client),
                selectinload(Work.narad),
                selectinload(Work.executor),
                selectinload(Work.catalog_item),
            )
            .order_by(Work.received_at.desc())
        )
        count_stmt = (
            select(func.count(Work.id))
            .select_from(Work)
            .join(Narad, Narad.id == Work.narad_id)
            .outerjoin(WorkCatalogItem, WorkCatalogItem.id == Work.work_catalog_item_id)
        )

        filters = []
        if order_number:
            filters.append(
                (Work.order_number.ilike(f"%{order_number}%"))
                | (Narad.doctor_name.ilike(f"%{order_number}%"))
                | (WorkCatalogItem.code.ilike(f"%{order_number}%"))
                | (WorkCatalogItem.name.ilike(f"%{order_number}%"))
                | (WorkCatalogItem.category.ilike(f"%{order_number}%"))
                | (Work.work_type.ilike(f"%{order_number}%"))
                | (Work.description.ilike(f"%{order_number}%"))
                | (Narad.doctor_phone.ilike(f"%{order_number}%"))
                | (Narad.patient_name.ilike(f"%{order_number}%"))
                | (Narad.patient_gender.ilike(f"%{order_number}%"))
                | (Narad.face_shape.ilike(f"%{order_number}%"))
                | (Narad.implant_system.ilike(f"%{order_number}%"))
                | (Narad.metal_type.ilike(f"%{order_number}%"))
                | (Narad.shade_color.ilike(f"%{order_number}%"))
                | (Narad.tooth_formula.ilike(f"%{order_number}%"))
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
            select(Work)
            .options(selectinload(Work.client), selectinload(Work.executor), selectinload(Work.narad))
            .where(Work.client_id == client_id)
        )
        return list(result.scalars().all())

    async def list_by_ids(self, work_ids: list[str]) -> list[Work]:
        if not work_ids:
            return []
        result = await self.session.execute(select(Work).where(Work.id.in_(work_ids)))
        return list(result.scalars().all())

    async def list_for_delivery(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        executor_id: str | None,
        sent: bool | None,
        ids: list[str] | None,
    ) -> tuple[list[Work], int]:
        stmt: Select = (
            select(Work)
            .join(Client, Client.id == Work.client_id)
            .join(Narad, Narad.id == Work.narad_id)
            .outerjoin(WorkCatalogItem, WorkCatalogItem.id == Work.work_catalog_item_id)
            .options(
                selectinload(Work.client),
                selectinload(Work.narad),
                selectinload(Work.executor),
                selectinload(Work.catalog_item),
            )
            .where(Work.status.in_([WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value]))
            .order_by(Work.delivery_sent.asc(), Client.name.asc(), Work.deadline_at.asc(), Work.received_at.desc())
        )
        count_stmt = (
            select(func.count(Work.id))
            .select_from(Work)
            .join(Client, Client.id == Work.client_id)
            .join(Narad, Narad.id == Work.narad_id)
            .outerjoin(WorkCatalogItem, WorkCatalogItem.id == Work.work_catalog_item_id)
            .where(Work.status.in_([WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value]))
        )

        filters = []
        if search:
            filters.append(
                or_(
                    Work.order_number.ilike(f"%{search}%"),
                    Narad.doctor_name.ilike(f"%{search}%"),
                    WorkCatalogItem.code.ilike(f"%{search}%"),
                    WorkCatalogItem.name.ilike(f"%{search}%"),
                    WorkCatalogItem.category.ilike(f"%{search}%"),
                    Work.work_type.ilike(f"%{search}%"),
                    Work.description.ilike(f"%{search}%"),
                    Narad.patient_name.ilike(f"%{search}%"),
                    Client.name.ilike(f"%{search}%"),
                    Client.contact_person.ilike(f"%{search}%"),
                    Client.phone.ilike(f"%{search}%"),
                    Client.address.ilike(f"%{search}%"),
                    Client.delivery_address.ilike(f"%{search}%"),
                    Client.delivery_contact.ilike(f"%{search}%"),
                    Client.delivery_phone.ilike(f"%{search}%"),
                )
            )
        if client_id:
            filters.append(Work.client_id == client_id)
        if executor_id:
            filters.append(Work.executor_id == executor_id)
        if sent is not None:
            filters.append(Work.delivery_sent.is_(sent))
        if ids:
            filters.append(Work.id.in_(ids))

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_for_delivery_by_ids(self, work_ids: list[str]) -> list[Work]:
        if not work_ids:
            return []

        result = await self.session.execute(
            select(Work)
            .options(
                selectinload(Work.client),
                selectinload(Work.narad),
                selectinload(Work.executor),
                selectinload(Work.catalog_item),
                selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
            )
            .where(Work.id.in_(work_ids))
        )
        works = {work.id: work for work in result.scalars().all()}
        return [works[work_id] for work_id in work_ids if work_id in works]

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Work]:
        result = await self.session.execute(
            select(Work)
            .options(
                selectinload(Work.client),
                selectinload(Work.executor),
                selectinload(Work.narad),
                selectinload(Work.catalog_item),
                selectinload(Work.work_items).selectinload(WorkItem.catalog_item),
                selectinload(Work.materials).selectinload(WorkMaterial.material),
                selectinload(Work.work_operations).selectinload(WorkOperation.executor),
                selectinload(Work.work_operations).selectinload(WorkOperation.executor_category),
                selectinload(Work.work_operations).selectinload(WorkOperation.logs),
                selectinload(Work.attachments),
                selectinload(Work.change_logs),
            )
            .order_by(Work.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_executor_payroll_summary(
        self,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
        executor_id: str | None = None,
    ) -> list[tuple[str, str, int, Decimal, Decimal]]:
        stmt: Select = (
            select(
                Executor.id,
                Executor.full_name,
                func.count(Work.id),
                func.coalesce(func.sum(Work.labor_cost), Decimal("0.00")),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")),
            )
            .join(Executor, Executor.id == Work.executor_id)
            .where(Work.executor_id.is_not(None))
            .where(Work.closed_at.is_not(None))
            .where(Work.status.in_([WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value]))
            .group_by(Executor.id)
            .order_by(func.coalesce(func.sum(Work.labor_cost), Decimal("0.00")).desc())
        )

        if date_from:
            stmt = stmt.where(Work.closed_at >= date_from)
        if date_to:
            stmt = stmt.where(Work.closed_at <= date_to)
        if executor_id:
            stmt = stmt.where(Work.executor_id == executor_id)

        result = await self.session.execute(stmt)
        return [(row[0], row[1], int(row[2]), row[3], row[4]) for row in result.all()]
