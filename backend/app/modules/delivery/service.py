from __future__ import annotations

from datetime import datetime, timezone

from app.common.enums import WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.work import Work, WorkChangeLog
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.delivery.schemas import (
    DeliveryItemRead,
    DeliveryListResponse,
    DeliveryMarkSentPayload,
    DeliveryMarkSentResponse,
)
from app.modules.delivery.templates import render_delivery_manifest_html


class DeliveryService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService, cache: CacheService):
        self._uow = uow
        self._search = search
        self._cache = cache

    async def list_delivery_items(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        executor_id: str | None,
        sent: bool | None,
    ) -> DeliveryListResponse:
        search_ids = await self._search.search_works(search) if search else None
        async with self._uow as uow:
            items, total_items = await uow.works.list_for_delivery(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                client_id=client_id,
                executor_id=executor_id,
                sent=sent,
                ids=search_ids if search_ids else None,
            )
            rows = [self._map_delivery_item(item) for item in items]
        return PaginatedResponse[DeliveryItemRead].create(
            rows,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    async def mark_sent(
        self,
        payload: DeliveryMarkSentPayload,
        *,
        actor_email: str | None = None,
    ) -> DeliveryMarkSentResponse:
        now = datetime.now(timezone.utc)
        async with self._uow as uow:
            works = await uow.works.list_for_delivery_by_ids(payload.work_ids)
            works_by_id = {work.id: work for work in works}
            missing_id = next((work_id for work_id in payload.work_ids if work_id not in works_by_id), None)
            if missing_id:
                raise NotFoundError("work", missing_id)

            updated_count = 0
            for work in works:
                if not work.delivery_sent:
                    updated_count += 1

                work.delivery_sent = True
                work.delivery_sent_at = work.delivery_sent_at or now
                work.status = WorkStatus.DELIVERED.value
                work.completed_at = work.completed_at or now
                await uow.works.add_change_log(
                    WorkChangeLog(
                        work_id=work.id,
                        action="delivery_marked_sent",
                        actor_email=actor_email,
                        details={
                            "delivery_sent": True,
                            "delivery_sent_at": work.delivery_sent_at.isoformat() if work.delivery_sent_at else None,
                            "status": work.status,
                        },
                    )
                )

            await uow.commit()
            rows = [self._map_delivery_item(work) for work in works]

        for work in works:
            await self._search.index_document(
                settings.elasticsearch_works_index,
                work.id,
                build_work_search_document(work),
            )
        await self._cache.invalidate_prefix("dashboard:")
        return DeliveryMarkSentResponse(updated_count=updated_count, items=rows)

    async def render_manifest(self, work_ids: list[str]) -> str:
        async with self._uow as uow:
            works = await uow.works.list_for_delivery_by_ids(work_ids)
            works_by_id = {work.id: work for work in works}
            missing_id = next((work_id for work_id in work_ids if work_id not in works_by_id), None)
            if missing_id:
                raise NotFoundError("work", missing_id)

            organization = await uow.organization.get_profile()
            if organization is None:
                raise NotFoundError("organization_profile", "default")

            rows = [self._map_delivery_item(works_by_id[work_id]) for work_id in work_ids if work_id in works_by_id]

        return render_delivery_manifest_html(
            {
                "organization": organization,
                "items": rows,
                "generated_at": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def _map_delivery_item(work: Work) -> DeliveryItemRead:
        return DeliveryItemRead(
            id=work.id,
            created_at=work.created_at,
            updated_at=work.updated_at,
            order_number=work.order_number,
            work_type=work.work_type,
            status=work.status,
            client_id=work.client_id,
            client_name=work.client.name,
            delivery_address=work.client.delivery_address or work.client.address,
            delivery_contact=work.client.delivery_contact or work.client.contact_person,
            delivery_phone=work.client.delivery_phone or work.client.phone,
            executor_id=work.executor_id,
            executor_name=work.executor.full_name if work.executor else None,
            doctor_name=work.doctor_name,
            patient_name=work.patient_name,
            received_at=work.received_at,
            deadline_at=work.deadline_at,
            completed_at=work.completed_at,
            delivery_sent=work.delivery_sent,
            delivery_sent_at=work.delivery_sent_at,
            price_for_client=work.price_for_client,
        )
