from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.common.enums import WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.work import Work, WorkMaterial
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.works.schemas import (
    WorkCompactRead,
    WorkCreate,
    WorkListResponse,
    WorkMaterialUsageRead,
    WorkRead,
    WorkUpdateStatus,
)


class WorkService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService, cache: CacheService):
        self._uow = uow
        self._search = search
        self._cache = cache

    async def list_works(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        client_id: str | None,
        executor_id: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> WorkListResponse:
        search_ids = await self._search.search_works(search) if search else None
        async with self._uow as uow:
            works, total_items = await uow.works.list(
                page=page,
                page_size=page_size,
                order_number=search if not search_ids else None,
                status=status,
                client_id=client_id,
                executor_id=executor_id,
                date_from=date_from,
                date_to=date_to,
                ids=search_ids if search_ids else None,
            )
            items = [WorkCompactRead.model_validate(work) for work in works]
        return PaginatedResponse[WorkCompactRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_work(self, work_id: str) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            return self._map_work_detail(work)

    async def create_work(self, payload: WorkCreate) -> WorkRead:
        async with self._uow as uow:
            existing_work = await uow.works.get_by_order_number(payload.order_number)
            if existing_work:
                raise ConflictError("Order number already exists.", code="order_number_exists")

            client = await uow.clients.get(payload.client_id)
            if client is None:
                raise NotFoundError("client", payload.client_id)

            executor = None
            labor_rate = Decimal("0.00")
            if payload.executor_id:
                executor = await uow.executors.get(payload.executor_id)
                if executor is None:
                    raise NotFoundError("executor", payload.executor_id)
                labor_rate = executor.hourly_rate

            material_ids = [material.material_id for material in payload.materials]
            materials = {material.id: material for material in await uow.materials.list_by_ids(material_ids)}
            material_names: list[str] = []
            material_cost = Decimal("0.00")
            material_entries: list[WorkMaterial] = []

            for usage in payload.materials:
                material = materials.get(usage.material_id)
                if material is None:
                    raise NotFoundError("material", usage.material_id)
                total_cost = material.average_price * usage.quantity
                material_cost += total_cost
                material_names.append(material.name)
                material_entries.append(
                    WorkMaterial(
                        material_id=material.id,
                        quantity=usage.quantity,
                        unit_cost=material.average_price,
                        total_cost=total_cost,
                    )
                )
                await uow.materials.consume_stock(material.id, usage.quantity)

            labor_cost = labor_rate * payload.labor_hours
            cost_price = material_cost + labor_cost + payload.additional_expenses
            margin = payload.price_for_client - cost_price

            work = await uow.works.add(
                Work(
                    order_number=payload.order_number,
                    client_id=payload.client_id,
                    executor_id=payload.executor_id,
                    work_type=payload.work_type,
                    description=payload.description,
                    status=payload.status.value,
                    received_at=payload.received_at,
                    deadline_at=payload.deadline_at,
                    price_for_client=payload.price_for_client,
                    cost_price=cost_price,
                    margin=margin,
                    additional_expenses=payload.additional_expenses,
                    labor_hours=payload.labor_hours,
                    amount_paid=payload.amount_paid,
                    comment=payload.comment,
                )
            )

            for item in material_entries:
                item.work_id = work.id
                await uow.works.add_material_usage(item)

            await uow.commit()

        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(
                work,
                client_name=client.name,
                executor_name=executor.full_name if executor else None,
                material_names=material_names,
            ),
        )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_work(work.id)

    async def update_status(self, work_id: str, payload: WorkUpdateStatus) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            work.status = payload.status.value
            if payload.status in {WorkStatus.COMPLETED, WorkStatus.DELIVERED}:
                work.completed_at = payload.completed_at or datetime.now(timezone.utc)
            await uow.commit()
            client_name = work.client.name

        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(work, client_name=client_name),
        )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_work(work_id)

    def _map_work_detail(self, work: Work) -> WorkRead:
        materials = [
            WorkMaterialUsageRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                material_id=item.material_id,
                material_name=item.material.name,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                total_cost=item.total_cost,
            )
            for item in work.materials
        ]
        return WorkRead(
            id=work.id,
            created_at=work.created_at,
            updated_at=work.updated_at,
            order_number=work.order_number,
            work_type=work.work_type,
            status=work.status,
            received_at=work.received_at,
            deadline_at=work.deadline_at,
            price_for_client=work.price_for_client,
            cost_price=work.cost_price,
            margin=work.margin,
            client_id=work.client_id,
            client_name=work.client.name,
            executor_id=work.executor_id,
            executor_name=work.executor.full_name if work.executor else None,
            description=work.description,
            completed_at=work.completed_at,
            additional_expenses=work.additional_expenses,
            labor_hours=work.labor_hours,
            amount_paid=work.amount_paid,
            comment=work.comment,
            materials=materials,
        )
