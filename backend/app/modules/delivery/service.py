from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.common.enums import WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.narad import Narad
from app.db.models.work import Work, WorkChangeLog
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.delivery.schemas import (
    DeliveryItemRead,
    DeliveryListResponse,
    DeliveryMarkSentPayload,
    DeliveryMarkSentResponse,
    DeliverySortBy,
    DeliverySortDirection,
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
        sort_by: DeliverySortBy,
        sort_direction: DeliverySortDirection,
    ) -> DeliveryListResponse:
        search_ids = await self._search.search_works(search) if search else None
        async with self._uow as uow:
            narad_ids = None
            if search_ids:
                works = await uow.works.list_by_ids(search_ids)
                narad_ids = list(dict.fromkeys(work.narad_id for work in works if getattr(work, "narad_id", None)))

            items, total_items = await uow.narads.list_for_delivery(
                page=page,
                page_size=page_size,
                search=search if not narad_ids else None,
                client_id=client_id,
                executor_id=executor_id,
                sent=sent,
                ids=narad_ids,
                sort_by=sort_by,
                sort_direction=sort_direction,
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
            narads = await uow.narads.list_for_delivery_by_ids(payload.narad_ids)
            narads_by_id = {narad.id: narad for narad in narads}
            missing_id = next((narad_id for narad_id in payload.narad_ids if narad_id not in narads_by_id), None)
            if missing_id:
                raise NotFoundError("narad", missing_id)

            updated_count = 0
            indexed_works: list[Work] = []
            for narad in narads:
                if not self._is_narad_delivery_sent(narad):
                    updated_count += 1

                for work in narad.works:
                    work.delivery_sent = True
                    work.delivery_sent_at = work.delivery_sent_at or now
                    work.status = WorkStatus.DELIVERED.value
                    work.completed_at = work.completed_at or now
                    indexed_works.append(work)
                    await uow.works.add_change_log(
                        WorkChangeLog(
                            work_id=work.id,
                            action="delivery_marked_sent",
                            actor_email=actor_email,
                            details={
                                "narad_id": narad.id,
                                "delivery_sent": True,
                                "delivery_sent_at": work.delivery_sent_at.isoformat() if work.delivery_sent_at else None,
                                "status": work.status,
                            },
                        )
                    )
                self._sync_narad_delivery_status(narad)

            await uow.commit()
            rows = [self._map_delivery_item(narad) for narad in narads]

        for work in indexed_works:
            await self._search.index_document(
                settings.elasticsearch_works_index,
                work.id,
                build_work_search_document(work),
            )
        await self._cache.invalidate_prefix("dashboard:")
        return DeliveryMarkSentResponse(updated_count=updated_count, items=rows)

    async def render_manifest(self, narad_ids: list[str]) -> str:
        async with self._uow as uow:
            narads = await uow.narads.list_for_delivery_by_ids(narad_ids)
            narads_by_id = {narad.id: narad for narad in narads}
            missing_id = next((narad_id for narad_id in narad_ids if narad_id not in narads_by_id), None)
            if missing_id:
                raise NotFoundError("narad", missing_id)

            organization = await uow.organization.get_profile()
            if organization is None:
                raise NotFoundError("organization_profile", "default")

            rows = [self._map_delivery_item(narads_by_id[narad_id]) for narad_id in narad_ids if narad_id in narads_by_id]

        return render_delivery_manifest_html(
            {
                "organization": organization,
                "items": rows,
                "generated_at": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def _map_delivery_item(narad: Narad) -> DeliveryItemRead:
        works = list(narad.works or [])
        work_numbers = [work.order_number for work in works]
        work_types = list(dict.fromkeys(work.work_type for work in works if work.work_type))
        executor_names = list(
            dict.fromkeys(work.executor.full_name for work in works if getattr(work, "executor", None) is not None)
        )
        total_price = sum((work.price_for_client for work in works), start=Decimal("0.00"))
        delivery_sent_at_values = [work.delivery_sent_at for work in works if work.delivery_sent_at is not None]
        delivery_sent = DeliveryService._is_narad_delivery_sent(narad)

        return DeliveryItemRead(
            id=narad.id,
            created_at=narad.created_at,
            updated_at=narad.updated_at,
            narad_number=narad.narad_number,
            title=narad.title,
            status=narad.status,
            client_id=narad.client_id,
            client_name=narad.client.name,
            delivery_address=narad.client.delivery_address or narad.client.address,
            delivery_contact=narad.client.delivery_contact or narad.client.contact_person,
            delivery_phone=narad.client.delivery_phone or narad.client.phone,
            works_count=len(works),
            work_numbers=work_numbers,
            work_types=work_types,
            executor_names=executor_names,
            doctor_name=narad.doctor_name,
            patient_name=narad.patient_name,
            received_at=narad.received_at,
            deadline_at=narad.deadline_at,
            completed_at=narad.completed_at,
            delivery_sent=delivery_sent,
            delivery_sent_at=max(delivery_sent_at_values) if delivery_sent and delivery_sent_at_values else None,
            total_price=total_price,
        )

    @staticmethod
    def _is_narad_delivery_sent(narad: Narad) -> bool:
        works = list(getattr(narad, "works", []) or [])
        return bool(works) and all(work.delivery_sent for work in works)

    @staticmethod
    def _sync_narad_delivery_status(narad: Narad) -> None:
        if DeliveryService._is_narad_delivery_sent(narad):
            narad.status = WorkStatus.DELIVERED.value
            narad.completed_at = narad.completed_at or max(
                (work.completed_at for work in narad.works if work.completed_at is not None),
                default=datetime.now(timezone.utc),
            )
