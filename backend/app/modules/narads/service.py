from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.common.enums import StockMovementType, WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.contractor import Contractor
from app.db.models.doctor import Doctor
from app.db.models.narad import Narad, NaradStatusLog
from app.db.models.payment import Payment
from app.db.models.work import Work, WorkChangeLog
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.narads.schemas import (
    NaradCompactRead,
    NaradClose,
    NaradCreate,
    NaradListResponse,
    OutsideWorkItemRead,
    OutsideWorkListResponse,
    OutsideWorkMarkReturned,
    OutsideWorkMarkSent,
    NaradPaymentRead,
    NaradReopen,
    NaradRead,
    NaradStatusLogRead,
    NaradUpdate,
    NaradWorkRead,
)
from app.modules.works.tooth_selection import build_tooth_formula_from_selection, serialize_tooth_selection


TWO_PLACES = Decimal("0.01")


class NaradService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService, cache: CacheService):
        self._uow = uow
        self._search = search
        self._cache = cache

    async def list_narads(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        client_id: str | None,
        date_from,
        date_to,
    ) -> NaradListResponse:
        async with self._uow as uow:
            narads, total_items = await uow.narads.list(
                page=page,
                page_size=page_size,
                search=search,
                status=status,
                client_id=client_id,
                date_from=date_from,
                date_to=date_to,
            )
            items = [self._map_narad_compact(item) for item in narads]
        return PaginatedResponse[NaradCompactRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_narad(self, narad_id: str) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            payments = await uow.payments.list_by_narad(narad_id, limit=20)
            return self._map_narad_detail(narad, payments=payments)

    async def list_outside_works(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        state: str | None,
    ) -> OutsideWorkListResponse:
        async with self._uow as uow:
            narads, total_items = await uow.narads.list_outside_works(
                page=page,
                page_size=page_size,
                search=search,
                client_id=client_id,
                state=state,
            )
            items = [self._map_outside_work_item(narad) for narad in narads]
        return PaginatedResponse[OutsideWorkItemRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def create_narad(self, payload: NaradCreate, *, actor_email: str | None = None) -> NaradRead:
        async with self._uow as uow:
            if await uow.narads.get_by_number(payload.narad_number):
                raise ConflictError("Narad number already exists.", code="narad_number_exists")

            client = await uow.clients.get(payload.client_id)
            if client is None:
                raise NotFoundError("client", payload.client_id)

            doctor = await self._resolve_doctor(uow, payload.client_id, payload.doctor_id)
            contractor = await self._resolve_contractor(uow, payload.contractor_id)
            narad = await uow.narads.add(
                Narad(
                    narad_number=payload.narad_number,
                    client_id=payload.client_id,
                    doctor_id=doctor.id if doctor else payload.doctor_id,
                    contractor_id=contractor.id if contractor else payload.contractor_id,
                    title=payload.title,
                    description=payload.description,
                    doctor_name=payload.doctor_name or (doctor.full_name if doctor else None),
                    doctor_phone=payload.doctor_phone or (doctor.phone if doctor else None),
                    patient_name=payload.patient_name,
                    patient_age=payload.patient_age,
                    patient_gender=payload.patient_gender.value if payload.patient_gender else None,
                    require_color_photo=payload.require_color_photo,
                    face_shape=payload.face_shape.value if payload.face_shape else None,
                    implant_system=payload.implant_system,
                    metal_type=payload.metal_type,
                    shade_color=payload.shade_color,
                    tooth_formula=payload.tooth_formula
                    or build_tooth_formula_from_selection(payload.tooth_selection),
                    tooth_selection=serialize_tooth_selection(payload.tooth_selection) or None,
                    status=WorkStatus.NEW.value,
                    received_at=payload.received_at,
                    deadline_at=payload.deadline_at,
                    is_outside_work=payload.is_outside_work,
                    outside_lab_name=contractor.name if contractor else payload.outside_lab_name,
                    outside_order_number=payload.outside_order_number,
                    outside_cost=payload.outside_cost,
                    outside_sent_at=payload.outside_sent_at,
                    outside_due_at=payload.outside_due_at,
                    outside_returned_at=payload.outside_returned_at,
                    outside_comment=payload.outside_comment,
                    completed_at=None,
                    closed_at=None,
                )
            )
            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="created",
                    actor_email=actor_email,
                    from_status=None,
                    to_status=narad.status,
                    details={"client_id": narad.client_id, "narad_number": narad.narad_number},
                )
            )
            await uow.commit()

        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad.id)

    async def update_narad(
        self,
        narad_id: str,
        payload: NaradUpdate,
        *,
        actor_email: str | None = None,
    ) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)

            payload_data = payload.model_dump(exclude_unset=True)
            next_client_id = payload_data.get("client_id", narad.client_id)
            if next_client_id != narad.client_id and narad.works:
                raise ConflictError(
                    "Narad client cannot be changed while it contains works.",
                    code="narad_client_change_forbidden",
                )

            next_number = payload_data.get("narad_number")
            if next_number and next_number != narad.narad_number:
                existing = await uow.narads.get_by_number(next_number)
                if existing is not None and existing.id != narad.id:
                    raise ConflictError("Narad number already exists.", code="narad_number_exists")

            doctor = await self._resolve_doctor(uow, next_client_id, payload_data.get("doctor_id", narad.doctor_id))
            contractor = await self._resolve_contractor(uow, payload_data.get("contractor_id", narad.contractor_id))

            narad.narad_number = payload_data.get("narad_number", narad.narad_number)
            narad.client_id = next_client_id
            narad.doctor_id = doctor.id if doctor else payload_data.get("doctor_id", narad.doctor_id)
            if "contractor_id" in payload_data:
                narad.contractor_id = contractor.id if contractor else payload_data.get("contractor_id")
            narad.title = payload_data.get("title", narad.title)
            narad.description = payload_data.get("description", narad.description)
            narad.doctor_name = payload_data.get("doctor_name", doctor.full_name if doctor else narad.doctor_name)
            narad.doctor_phone = payload_data.get("doctor_phone", doctor.phone if doctor else narad.doctor_phone)
            narad.patient_name = payload_data.get("patient_name", narad.patient_name)
            narad.patient_age = payload_data.get("patient_age", narad.patient_age)
            if "patient_gender" in payload_data:
                patient_gender = payload_data.get("patient_gender")
                narad.patient_gender = patient_gender.value if patient_gender is not None else None
            if "require_color_photo" in payload_data:
                narad.require_color_photo = bool(payload_data["require_color_photo"])
            if "face_shape" in payload_data:
                face_shape = payload_data.get("face_shape")
                narad.face_shape = face_shape.value if face_shape is not None else None
            if "implant_system" in payload_data:
                narad.implant_system = payload_data.get("implant_system")
            if "metal_type" in payload_data:
                narad.metal_type = payload_data.get("metal_type")
            if "shade_color" in payload_data:
                narad.shade_color = payload_data.get("shade_color")
            if "tooth_selection" in payload_data:
                serialized_tooth_selection = serialize_tooth_selection(payload_data["tooth_selection"] or [])
                narad.tooth_selection = serialized_tooth_selection or None
                narad.tooth_formula = payload_data.get("tooth_formula") or build_tooth_formula_from_selection(
                    serialized_tooth_selection
                )
            elif "tooth_formula" in payload_data:
                narad.tooth_formula = payload_data.get("tooth_formula")
            narad.received_at = payload_data.get("received_at", narad.received_at)
            narad.deadline_at = payload_data.get("deadline_at", narad.deadline_at)
            if "is_outside_work" in payload_data:
                narad.is_outside_work = bool(payload_data["is_outside_work"])
            if "outside_lab_name" in payload_data:
                narad.outside_lab_name = contractor.name if contractor else payload_data.get("outside_lab_name")
            if "outside_order_number" in payload_data:
                narad.outside_order_number = payload_data.get("outside_order_number")
            if "outside_cost" in payload_data and payload_data.get("outside_cost") is not None:
                narad.outside_cost = payload_data["outside_cost"]
            if "outside_sent_at" in payload_data:
                narad.outside_sent_at = payload_data.get("outside_sent_at")
            if "outside_due_at" in payload_data:
                narad.outside_due_at = payload_data.get("outside_due_at")
            if "outside_returned_at" in payload_data:
                narad.outside_returned_at = payload_data.get("outside_returned_at")
            if "outside_comment" in payload_data:
                narad.outside_comment = payload_data.get("outside_comment")

            if "contractor_id" in payload_data and contractor is not None:
                narad.outside_lab_name = contractor.name

            if not narad.is_outside_work:
                narad.contractor_id = None
                narad.outside_lab_name = None
                narad.outside_order_number = None
                narad.outside_cost = Decimal("0.00")
                narad.outside_sent_at = None
                narad.outside_due_at = None
                narad.outside_returned_at = None
                narad.outside_comment = None

            for work in narad.works:
                work.received_at = narad.received_at
                work.deadline_at = narad.deadline_at

            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="updated",
                    actor_email=actor_email,
                    from_status=narad.status,
                    to_status=narad.status,
                    details={
                        "narad_number": narad.narad_number,
                        "client_id": narad.client_id,
                        "doctor_id": narad.doctor_id,
                    },
                )
            )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    async def reserve_materials(self, narad_id: str, *, actor_email: str | None = None) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if narad.closed_at is not None:
                raise ConflictError("Closed narad cannot reserve materials.", code="narad_closed_for_reserve")
            if not narad.works:
                raise ConflictError("Narad has no works for reservation.", code="narad_has_no_works")

            reserved_lines = await self._reserve_narad_materials(uow, narad)
            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="materials_reserved",
                    actor_email=actor_email,
                    from_status=narad.status,
                    to_status=narad.status,
                    details={"reserved_lines": reserved_lines},
                )
            )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    async def close_narad(
        self,
        narad_id: str,
        payload: NaradClose,
        *,
        actor_email: str | None = None,
    ) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if narad.closed_at is not None:
                raise ConflictError("Narad is already closed.", code="narad_already_closed")
            if not narad.works:
                raise ConflictError("Narad has no works to close.", code="narad_has_no_works")

            now = datetime.now(timezone.utc)
            previous_status = narad.status
            stock_action = "none"
            if payload.status == WorkStatus.CANCELLED:
                await self._release_narad_materials(uow, narad)
                stock_action = "released"
            else:
                await self._consume_narad_materials(uow, narad)
                stock_action = "consumed"

            for work in narad.works:
                if work.closed_at is None:
                    work.status = payload.status.value
                    if payload.status in {WorkStatus.COMPLETED, WorkStatus.DELIVERED}:
                        work.completed_at = payload.completed_at or work.completed_at or now
                    else:
                        work.completed_at = None
                    work.closed_at = now
                if payload.status == WorkStatus.DELIVERED:
                    work.delivery_sent = True
                    work.delivery_sent_at = work.delivery_sent_at or now
                elif payload.status != WorkStatus.DELIVERED:
                    work.delivery_sent = False
                    work.delivery_sent_at = None

            self._sync_narad_lifecycle(narad)
            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="closed",
                    actor_email=actor_email,
                    from_status=previous_status,
                    to_status=narad.status,
                    note=payload.note,
                    details={"stock_action": stock_action},
                )
            )
            for work in narad.works:
                await uow.works.add_change_log(
                    WorkChangeLog(
                        work_id=work.id,
                        action="narad_closed",
                        actor_email=actor_email,
                        details={
                            "narad_id": narad.id,
                            "narad_number": narad.narad_number,
                            "status": work.status,
                            "note": payload.note,
                            "stock_action": stock_action,
                        },
                    )
                )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    async def reopen_narad(
        self,
        narad_id: str,
        payload: NaradReopen,
        *,
        actor_email: str | None = None,
    ) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if narad.closed_at is None:
                raise ConflictError("Narad is not closed.", code="narad_not_closed")

            previous_status = narad.status
            await self._restore_narad_materials(uow, narad)

            for work in narad.works:
                if work.closed_at is not None:
                    work.status = payload.status.value
                    work.closed_at = None
                    if payload.status not in {WorkStatus.COMPLETED, WorkStatus.DELIVERED}:
                        work.completed_at = None
                if payload.status != WorkStatus.DELIVERED:
                    work.delivery_sent = False
                    work.delivery_sent_at = None

            self._sync_narad_lifecycle(narad)
            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="reopened",
                    actor_email=actor_email,
                    from_status=previous_status,
                    to_status=narad.status,
                    note=payload.note,
                    details={"stock_action": "restored"},
                )
            )
            for work in narad.works:
                await uow.works.add_change_log(
                    WorkChangeLog(
                        work_id=work.id,
                        action="narad_reopened",
                        actor_email=actor_email,
                        details={
                            "narad_id": narad.id,
                            "narad_number": narad.narad_number,
                            "status": work.status,
                            "note": payload.note,
                            "stock_action": "restored",
                        },
                    )
                )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    async def mark_outside_sent(
        self,
        narad_id: str,
        payload: OutsideWorkMarkSent,
        *,
        actor_email: str | None = None,
    ) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if narad.closed_at is not None:
                raise ConflictError("Closed narad cannot be sent to outside work.", code="narad_closed_for_outside_work")

            narad.is_outside_work = True
            contractor = await self._resolve_contractor(uow, payload.contractor_id)
            narad.contractor_id = contractor.id if contractor else None
            narad.outside_lab_name = contractor.name if contractor else payload.outside_lab_name
            narad.outside_order_number = payload.outside_order_number
            narad.outside_cost = payload.outside_cost
            narad.outside_sent_at = payload.outside_sent_at
            narad.outside_due_at = payload.outside_due_at
            narad.outside_returned_at = None
            narad.outside_comment = payload.outside_comment

            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="outside_sent",
                    actor_email=actor_email,
                    from_status=narad.status,
                    to_status=narad.status,
                    details={
                        "outside_lab_name": narad.outside_lab_name,
                        "outside_order_number": narad.outside_order_number,
                        "outside_cost": str(narad.outside_cost),
                        "outside_sent_at": narad.outside_sent_at.isoformat() if narad.outside_sent_at else None,
                        "outside_due_at": narad.outside_due_at.isoformat() if narad.outside_due_at else None,
                    },
                )
            )
            for work in narad.works:
                await uow.works.add_change_log(
                    WorkChangeLog(
                        work_id=work.id,
                        action="outside_sent",
                        actor_email=actor_email,
                        details={
                            "narad_id": narad.id,
                            "narad_number": narad.narad_number,
                            "outside_lab_name": narad.outside_lab_name,
                            "outside_order_number": narad.outside_order_number,
                        },
                    )
                )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    async def mark_outside_returned(
        self,
        narad_id: str,
        payload: OutsideWorkMarkReturned,
        *,
        actor_email: str | None = None,
    ) -> NaradRead:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if not narad.is_outside_work or narad.outside_sent_at is None:
                raise ConflictError("Narad is not currently in outside work.", code="narad_not_in_outside_work")
            if narad.outside_returned_at is not None:
                raise ConflictError("Narad is already returned from outside work.", code="narad_already_returned")

            narad.outside_returned_at = payload.outside_returned_at
            narad.outside_comment = payload.outside_comment or narad.outside_comment

            await uow.narads.add_status_log(
                NaradStatusLog(
                    narad_id=narad.id,
                    action="outside_returned",
                    actor_email=actor_email,
                    from_status=narad.status,
                    to_status=narad.status,
                    details={
                        "outside_lab_name": narad.outside_lab_name,
                        "outside_returned_at": narad.outside_returned_at.isoformat()
                        if narad.outside_returned_at
                        else None,
                    },
                )
            )
            for work in narad.works:
                await uow.works.add_change_log(
                    WorkChangeLog(
                        work_id=work.id,
                        action="outside_returned",
                        actor_email=actor_email,
                        details={
                            "narad_id": narad.id,
                            "narad_number": narad.narad_number,
                            "outside_returned_at": narad.outside_returned_at.isoformat()
                            if narad.outside_returned_at
                            else None,
                        },
                    )
                )
            await uow.commit()
            work_ids = [work.id for work in narad.works]

        for work_id in work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_narad(narad_id)

    def _map_narad_compact(self, narad: Narad) -> NaradCompactRead:
        totals = self._calculate_totals(narad, narad.works)
        return NaradCompactRead(
            id=narad.id,
            created_at=narad.created_at,
            updated_at=narad.updated_at,
            narad_number=narad.narad_number,
            title=narad.title,
            client_id=narad.client_id,
            client_name=narad.client.name,
            client_email=getattr(narad.client, "email", None),
            doctor_id=narad.doctor_id,
            doctor_name=narad.doctor_name,
            doctor_phone=narad.doctor_phone,
            contractor_id=narad.contractor_id,
            contractor_name=narad.contractor.name if narad.contractor else narad.outside_lab_name,
            patient_name=narad.patient_name,
            require_color_photo=narad.require_color_photo,
            face_shape=narad.face_shape,
            implant_system=narad.implant_system,
            metal_type=narad.metal_type,
            shade_color=narad.shade_color,
            tooth_formula=narad.tooth_formula,
            status=narad.status,
            received_at=narad.received_at,
            deadline_at=narad.deadline_at,
            completed_at=narad.completed_at,
            closed_at=narad.closed_at,
            is_outside_work=narad.is_outside_work,
            outside_lab_name=narad.outside_lab_name,
            outside_order_number=narad.outside_order_number,
            outside_cost=narad.outside_cost,
            outside_sent_at=narad.outside_sent_at,
            outside_due_at=narad.outside_due_at,
            outside_returned_at=narad.outside_returned_at,
            outside_comment=narad.outside_comment,
            is_closed=narad.closed_at is not None,
            works_count=len(narad.works),
            total_price=totals["total_price"],
            total_cost=totals["total_cost"],
            total_margin=totals["total_margin"],
            amount_paid=totals["amount_paid"],
            balance_due=totals["balance_due"],
        )

    def _map_narad_detail(self, narad: Narad, *, payments: list[Payment] | None = None) -> NaradRead:
        compact = self._map_narad_compact(narad)
        works = [
            NaradWorkRead(
                id=work.id,
                created_at=work.created_at,
                updated_at=work.updated_at,
                order_number=work.order_number,
                work_type=work.work_type,
                status=work.status,
                executor_id=work.executor_id,
                executor_name=work.executor.full_name if work.executor else None,
                work_catalog_item_code=work.catalog_item.code if work.catalog_item else None,
                work_catalog_item_name=work.catalog_item.name if work.catalog_item else None,
                price_for_client=work.price_for_client,
                cost_price=work.cost_price,
                margin=work.margin,
                amount_paid=work.amount_paid,
                balance_due=max(work.price_for_client - work.amount_paid, Decimal("0.00")).quantize(TWO_PLACES),
                received_at=work.received_at,
                deadline_at=work.deadline_at,
                completed_at=work.completed_at,
                closed_at=work.closed_at,
            )
            for work in sorted(narad.works, key=lambda item: (item.received_at, item.created_at))
        ]
        status_logs = [
            NaradStatusLogRead(
                id=log.id,
                created_at=log.created_at,
                updated_at=log.updated_at,
                action=log.action,
                actor_email=log.actor_email,
                from_status=log.from_status,
                to_status=log.to_status,
                note=log.note,
                details=log.details or {},
            )
            for log in narad.status_logs
        ]
        payment_reads: list[NaradPaymentRead] = []
        for payment in payments or []:
            amount_allocated = sum(
                (
                    allocation.amount
                    for allocation in payment.allocations
                    if allocation.work and allocation.work.narad_id == narad.id
                ),
                start=Decimal("0.00"),
            ).quantize(TWO_PLACES)
            if amount_allocated <= 0:
                continue
            payment_reads.append(
                NaradPaymentRead(
                    id=payment.id,
                    created_at=payment.created_at,
                    updated_at=payment.updated_at,
                    payment_number=payment.payment_number,
                    payment_date=payment.payment_date,
                    method=payment.method,
                    amount=payment.amount,
                    amount_allocated_to_narad=amount_allocated,
                    external_reference=payment.external_reference,
                    comment=payment.comment,
                )
            )
        return NaradRead(
            **compact.model_dump(),
            description=narad.description,
            patient_age=narad.patient_age,
            patient_gender=narad.patient_gender,
            tooth_selection=narad.tooth_selection or [],
            works=works,
            payments=payment_reads,
            status_logs=status_logs,
        )

    def _map_outside_work_item(self, narad: Narad) -> OutsideWorkItemRead:
        works = list(narad.works)
        outside_status = self._resolve_outside_status(narad)
        return OutsideWorkItemRead(
            narad_id=narad.id,
            narad_number=narad.narad_number,
            title=narad.title,
            client_name=narad.client.name,
            contractor_id=narad.contractor_id,
            contractor_name=narad.contractor.name if narad.contractor else narad.outside_lab_name,
            patient_name=narad.patient_name,
            doctor_name=narad.doctor_name,
            status=narad.status,
            works_count=len(works),
            work_numbers=[work.order_number for work in works],
            work_types=[work.work_type for work in works],
            outside_lab_name=narad.outside_lab_name,
            outside_order_number=narad.outside_order_number,
            outside_cost=narad.outside_cost,
            outside_sent_at=narad.outside_sent_at,
            outside_due_at=narad.outside_due_at,
            outside_returned_at=narad.outside_returned_at,
            outside_comment=narad.outside_comment,
            outside_status=outside_status,
            is_outside_overdue=outside_status == "overdue",
            received_at=narad.received_at,
            deadline_at=narad.deadline_at,
        )

    @staticmethod
    def _calculate_totals(narad: Narad, works: list[Work]) -> dict[str, Decimal]:
        total_price = sum((work.price_for_client for work in works), Decimal("0.00")).quantize(TWO_PLACES)
        inside_total_cost = sum((work.cost_price for work in works), Decimal("0.00")).quantize(TWO_PLACES)
        inside_total_margin = sum((work.margin for work in works), Decimal("0.00")).quantize(TWO_PLACES)
        outside_cost = (narad.outside_cost or Decimal("0.00")).quantize(TWO_PLACES)
        total_cost = (inside_total_cost + outside_cost).quantize(TWO_PLACES)
        total_margin = (inside_total_margin - outside_cost).quantize(TWO_PLACES)
        amount_paid = sum((work.amount_paid for work in works), Decimal("0.00")).quantize(TWO_PLACES)
        return {
            "total_price": total_price,
            "total_cost": total_cost,
            "total_margin": total_margin,
            "amount_paid": amount_paid,
            "balance_due": max(total_price - amount_paid, Decimal("0.00")).quantize(TWO_PLACES),
        }

    @staticmethod
    async def _resolve_doctor(
        uow: SQLAlchemyUnitOfWork,
        client_id: str,
        doctor_id: str | None,
    ) -> Doctor | None:
        if not doctor_id:
            return None
        doctor = await uow.doctors.get(doctor_id)
        if doctor is None:
            raise NotFoundError("doctor", doctor_id)
        if doctor.client_id != client_id:
            raise ConflictError("Doctor must belong to the selected client.", code="narad_doctor_client_mismatch")
        return doctor

    @staticmethod
    async def _resolve_contractor(
        uow: SQLAlchemyUnitOfWork,
        contractor_id: str | None,
    ) -> Contractor | None:
        if not contractor_id:
            return None
        contractor = await uow.contractors.get(contractor_id)
        if contractor is None:
            raise NotFoundError("contractor", contractor_id)
        return contractor

    async def _reindex_work(self, work_id: str) -> None:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                return
        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(
                work,
                client_name=work.client.name if work.client else None,
                executor_name=work.executor.full_name if work.executor else None,
                doctor_name=work.narad.doctor_name if work.narad else None,
                work_catalog_item_name=work.catalog_item.name if work.catalog_item else None,
                work_catalog_item_code=work.catalog_item.code if work.catalog_item else None,
                work_catalog_item_category=work.catalog_item.category if work.catalog_item else None,
                work_item_types=[item.work_type for item in work.work_items if item.work_type],
                work_item_codes=[item.catalog_item.code for item in work.work_items if item.catalog_item and item.catalog_item.code],
                work_item_descriptions=[item.description for item in work.work_items if item.description],
                operation_names=[item.operation_name for item in work.work_operations if item.operation_name],
                material_names=[item.material.name for item in work.materials if item.material and item.material.name],
            ),
        )

    @staticmethod
    async def _reserve_narad_materials(uow: SQLAlchemyUnitOfWork, narad: Narad) -> int:
        reserved_lines = 0
        for work in narad.works:
            for item in work.materials:
                if item.reserved_at is not None or item.consumed_at is not None:
                    continue
                await uow.materials.change_reserved_stock(
                    item.material_id,
                    quantity_delta=item.quantity,
                    movement_type=StockMovementType.RESERVE.value,
                    comment=f"Резерв под наряд {narad.narad_number} / заказ {work.order_number}",
                    work_id=work.id,
                )
                item.reserved_at = datetime.now(timezone.utc)
                reserved_lines += 1
        return reserved_lines

    @staticmethod
    async def _release_narad_materials(uow: SQLAlchemyUnitOfWork, narad: Narad) -> int:
        released_lines = 0
        for work in narad.works:
            for item in work.materials:
                if item.reserved_at is None or item.consumed_at is not None:
                    continue
                await uow.materials.change_reserved_stock(
                    item.material_id,
                    quantity_delta=-item.quantity,
                    movement_type=StockMovementType.RELEASE.value,
                    comment=f"Снятие резерва по наряду {narad.narad_number} / заказ {work.order_number}",
                    work_id=work.id,
                )
                item.reserved_at = None
                released_lines += 1
        return released_lines

    @staticmethod
    async def _consume_narad_materials(uow: SQLAlchemyUnitOfWork, narad: Narad) -> int:
        consumed_lines = 0
        for work in narad.works:
            for item in work.materials:
                if item.consumed_at is not None:
                    continue
                if item.reserved_at is not None:
                    await uow.materials.change_reserved_stock(
                        item.material_id,
                        quantity_delta=-item.quantity,
                        movement_type=StockMovementType.RELEASE.value,
                        comment=f"Использован резерв по наряду {narad.narad_number} / заказ {work.order_number}",
                        work_id=work.id,
                    )
                await uow.materials.change_stock(
                    item.material_id,
                    quantity_delta=-item.quantity,
                    movement_type=StockMovementType.CONSUME.value,
                    unit_cost=item.unit_cost,
                    comment=f"Списание при закрытии наряда {narad.narad_number} / заказ {work.order_number}",
                    work_id=work.id,
                    respect_reservations=item.reserved_at is None,
                )
                item.consumed_at = datetime.now(timezone.utc)
                consumed_lines += 1
        return consumed_lines

    @staticmethod
    async def _restore_narad_materials(uow: SQLAlchemyUnitOfWork, narad: Narad) -> int:
        restored_lines = 0
        for work in narad.works:
            for item in work.materials:
                if item.consumed_at is None:
                    continue
                await uow.materials.change_stock(
                    item.material_id,
                    quantity_delta=item.quantity,
                    movement_type=StockMovementType.RESTORE.value,
                    unit_cost=item.unit_cost,
                    comment=f"Возврат при повторном открытии наряда {narad.narad_number} / заказ {work.order_number}",
                    work_id=work.id,
                    respect_reservations=False,
                )
                if item.reserved_at is not None:
                    await uow.materials.change_reserved_stock(
                        item.material_id,
                        quantity_delta=item.quantity,
                        movement_type=StockMovementType.RESERVE.value,
                        comment=f"Повторный резерв после открытия наряда {narad.narad_number} / заказ {work.order_number}",
                        work_id=work.id,
                    )
                item.consumed_at = None
                restored_lines += 1
        return restored_lines

    @staticmethod
    def _sync_narad_lifecycle(narad: Narad) -> None:
        works = list(narad.works)
        if not works:
            narad.status = WorkStatus.NEW.value
            narad.completed_at = None
            narad.closed_at = None
            return

        statuses = [work.status for work in works]
        narad.received_at = min(work.received_at for work in works)
        deadlines = [work.deadline_at for work in works if work.deadline_at is not None]
        narad.deadline_at = max(deadlines) if deadlines else None

        if all(status == WorkStatus.CANCELLED.value for status in statuses):
            narad.status = WorkStatus.CANCELLED.value
        elif all(status == WorkStatus.DELIVERED.value for status in statuses):
            narad.status = WorkStatus.DELIVERED.value
        elif all(status in {WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value} for status in statuses):
            narad.status = WorkStatus.COMPLETED.value
        elif any(status == WorkStatus.IN_REVIEW.value for status in statuses):
            narad.status = WorkStatus.IN_REVIEW.value
        elif any(status in {WorkStatus.IN_PROGRESS.value, WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value} for status in statuses):
            narad.status = WorkStatus.IN_PROGRESS.value
        else:
            narad.status = WorkStatus.NEW.value

        completed_values = [work.completed_at for work in works if work.completed_at is not None]
        narad.completed_at = max(completed_values) if len(completed_values) == len(works) else None
        closed_values = [work.closed_at for work in works if work.closed_at is not None]
        narad.closed_at = max(closed_values) if len(closed_values) == len(works) else None

    @staticmethod
    def _resolve_outside_status(narad: Narad) -> str:
        if narad.outside_returned_at is not None:
            return "returned"
        if narad.outside_due_at is not None and narad.outside_due_at < datetime.now(timezone.utc):
            return "overdue"
        return "sent"
