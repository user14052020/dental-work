from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.common.attachments import WorkAttachmentStorage
from app.common.enums import OperationExecutionStatus, WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.operation import WorkOperation, WorkOperationLog
from app.db.models.work import Work, WorkAttachment, WorkChangeLog, WorkItem, WorkMaterial
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.operations.schemas import WorkOperationLogRead, WorkOperationRead, WorkOperationStatusUpdate
from app.modules.works.schemas import (
    ExecutorPayrollItemRead,
    WorkAttachmentRead,
    WorkClose,
    WorkCompactRead,
    WorkChangeLogRead,
    WorkCreate,
    WorkItemRead,
    WorkListResponse,
    WorkMaterialUsageRead,
    WorkPayrollSummaryRead,
    WorkRead,
    WorkReopen,
    WorkUpdateStatus,
)
from app.modules.works.tooth_selection import build_tooth_formula_from_selection, serialize_tooth_selection


TWO_PLACES = Decimal("0.01")


class WorkService:
    def __init__(
        self,
        uow: SQLAlchemyUnitOfWork,
        search: SearchService,
        cache: CacheService,
        attachments: WorkAttachmentStorage | None = None,
    ):
        self._uow = uow
        self._search = search
        self._cache = cache
        self._attachments = attachments or WorkAttachmentStorage()

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

    async def create_work(self, payload: WorkCreate, *, actor_email: str | None = None) -> WorkRead:
        async with self._uow as uow:
            existing_work = await uow.works.get_by_order_number(payload.order_number)
            if existing_work:
                raise ConflictError("Order number already exists.", code="order_number_exists")

            client = await uow.clients.get(payload.client_id)
            if client is None:
                raise NotFoundError("client", payload.client_id)

            doctor = None
            if payload.doctor_id:
                doctor = await uow.doctors.get(payload.doctor_id)
                if doctor is None:
                    raise NotFoundError("doctor", payload.doctor_id)

            catalog_item_ids = {
                catalog_item_id
                for catalog_item_id in [
                    payload.work_catalog_item_id,
                    *[item.work_catalog_item_id for item in payload.work_items],
                ]
                if catalog_item_id
            }
            catalog_items_by_id = {}
            for catalog_item_id in catalog_item_ids:
                resolved_catalog_item = await uow.work_catalog.get(catalog_item_id)
                if resolved_catalog_item is None:
                    raise NotFoundError("work_catalog_item", catalog_item_id)
                catalog_items_by_id[catalog_item_id] = resolved_catalog_item

            client_catalog_prices = {
                item.work_catalog_item_id: item for item in getattr(client, "catalog_prices", [])
            }
            catalog_item = catalog_items_by_id.get(payload.work_catalog_item_id) if payload.work_catalog_item_id else None
            client_catalog_price = client_catalog_prices.get(catalog_item.id) if catalog_item else None

            executor_ids = {
                executor_id
                for executor_id in [payload.executor_id, *[operation.executor_id for operation in payload.operations]]
                if executor_id
            }
            executors_by_id = {}
            for executor_id in executor_ids:
                resolved_executor = await uow.executors.get(executor_id)
                if resolved_executor is None:
                    raise NotFoundError("executor", executor_id)
                executors_by_id[executor_id] = resolved_executor

            executor = executors_by_id.get(payload.executor_id) if payload.executor_id else None
            labor_rate = executor.hourly_rate if executor else Decimal("0.00")

            resolved_work_items_data: list[dict[str, object]] = []
            if payload.work_items:
                for index, item_payload in enumerate(payload.work_items):
                    item_catalog = (
                        catalog_items_by_id.get(item_payload.work_catalog_item_id)
                        if item_payload.work_catalog_item_id
                        else None
                    )
                    item_client_price = (
                        client_catalog_prices.get(item_catalog.id)
                        if item_catalog is not None
                        else None
                    )
                    resolved_item_work_type = item_payload.work_type or (item_catalog.name if item_catalog else None)
                    if not resolved_item_work_type:
                        raise ConflictError("Each work item must have a work type.", code="work_item_type_required")

                    resolved_unit_price = item_payload.unit_price
                    if resolved_unit_price is None and item_catalog is not None:
                        resolved_unit_price = (
                            item_client_price.price
                            if item_client_price is not None
                            else item_catalog.base_price
                        )
                    if resolved_unit_price is None:
                        raise ConflictError(
                            "Each work item without catalog link must have a unit price.",
                            code="work_item_price_required",
                        )

                    quantity = item_payload.quantity.quantize(TWO_PLACES)
                    unit_price = resolved_unit_price.quantize(TWO_PLACES)
                    resolved_work_items_data.append(
                        {
                            "catalog_item": item_catalog,
                            "work_catalog_item_id": item_catalog.id if item_catalog else item_payload.work_catalog_item_id,
                            "work_type": resolved_item_work_type,
                            "description": item_payload.description or (item_catalog.description if item_catalog else None),
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "total_price": (unit_price * quantity).quantize(TWO_PLACES),
                            "sort_order": index,
                        }
                    )

                summary_item = resolved_work_items_data[0]
                catalog_item = summary_item["catalog_item"]  # type: ignore[assignment]
                resolved_work_type = str(summary_item["work_type"])
                base_price = sum(
                    (Decimal(str(item["total_price"])) for item in resolved_work_items_data),
                    start=Decimal("0.00"),
                ).quantize(TWO_PLACES)
                adjustment_percent = Decimal("0.00")
                price_for_client = base_price
                work_description = payload.description or summary_item["description"]
            else:
                resolved_work_type = payload.work_type or (catalog_item.name if catalog_item else None)
                if not resolved_work_type:
                    raise ConflictError("Work type is required.", code="work_type_required")

                resolved_base_price = payload.base_price_for_client
                if resolved_base_price is None and catalog_item is not None:
                    resolved_base_price = (
                        client_catalog_price.price
                        if client_catalog_price is not None
                        else catalog_item.base_price
                    )

                if resolved_base_price is None and payload.price_adjustment_percent is None:
                    base_price = payload.price_for_client
                    adjustment_percent = Decimal("0.00")
                    price_for_client = payload.price_for_client
                else:
                    base_price = (
                        resolved_base_price
                        if resolved_base_price is not None
                        else payload.price_for_client
                    )
                    adjustment_percent = self._resolve_adjustment_percent(
                        payload.price_adjustment_percent,
                        Decimal("0.00") if client_catalog_price is not None else client.default_price_adjustment_percent,
                    )
                    price_for_client = self._calculate_price(base_price, adjustment_percent)

                resolved_work_items_data.append(
                    {
                        "catalog_item": catalog_item,
                        "work_catalog_item_id": catalog_item.id if catalog_item else payload.work_catalog_item_id,
                        "work_type": resolved_work_type,
                        "description": payload.description,
                        "quantity": Decimal("1.00"),
                        "unit_price": price_for_client,
                        "total_price": price_for_client,
                        "sort_order": 0,
                    }
                )
                work_description = payload.description

            tooth_selection = serialize_tooth_selection(payload.tooth_selection)
            tooth_formula = payload.tooth_formula or build_tooth_formula_from_selection(tooth_selection)
            operation_ids = [item.operation_id for item in payload.operations]
            operations_catalog = {
                item.id: item for item in await uow.operations.list_operations_by_ids(operation_ids)
            }

            material_ids = [material.material_id for material in payload.materials]
            materials = {material.id: material for material in await uow.materials.list_by_ids(material_ids)}
            material_names: list[str] = []
            material_cost = Decimal("0.00")
            material_entries: list[WorkMaterial] = []
            operation_names: list[str] = []
            work_operations: list[WorkOperation] = []

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

            if payload.operations:
                labor_cost = Decimal("0.00")
                for index, operation_item in enumerate(payload.operations):
                    operation_catalog = operations_catalog.get(operation_item.operation_id)
                    if operation_catalog is None:
                        raise NotFoundError("operation", operation_item.operation_id)

                    line_executor = executors_by_id.get(operation_item.executor_id) if operation_item.executor_id else executor
                    line_category = line_executor.payment_category if line_executor else None
                    category_rate_map = {
                        rate.executor_category_id: rate.labor_rate
                        for rate in operation_catalog.payment_rates
                    }
                    unit_labor_cost = (
                        operation_item.unit_labor_cost_override
                        if operation_item.unit_labor_cost_override is not None
                        else category_rate_map.get(line_category.id if line_category else "", Decimal("0.00"))
                    )
                    total_labor_cost = (unit_labor_cost * operation_item.quantity).quantize(TWO_PLACES)
                    labor_cost += total_labor_cost
                    operation_names.append(operation_catalog.name)
                    work_operations.append(
                        WorkOperation(
                            operation_id=operation_catalog.id,
                            executor_id=line_executor.id if line_executor else None,
                            executor_category_id=line_category.id if line_category else None,
                            operation_code=operation_catalog.code,
                            operation_name=operation_catalog.name,
                            quantity=operation_item.quantity,
                            unit_labor_cost=unit_labor_cost,
                            total_labor_cost=total_labor_cost,
                            status=OperationExecutionStatus.PLANNED.value,
                            sort_order=index,
                            manual_rate_override=operation_item.unit_labor_cost_override is not None,
                            note=operation_item.note,
                        )
                    )
                labor_cost = labor_cost.quantize(TWO_PLACES)
            else:
                labor_cost = (labor_rate * payload.labor_hours).quantize(TWO_PLACES)
            cost_price = material_cost + labor_cost + payload.additional_expenses
            margin = price_for_client - cost_price

            work = await uow.works.add(
                Work(
                    order_number=payload.order_number,
                    client_id=payload.client_id,
                    executor_id=payload.executor_id,
                    doctor_id=payload.doctor_id,
                    work_catalog_item_id=catalog_item.id if catalog_item else payload.work_catalog_item_id,
                    work_type=resolved_work_type,
                    description=work_description,
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
                    tooth_formula=tooth_formula,
                    tooth_selection=tooth_selection or None,
                    status=payload.status.value,
                    received_at=payload.received_at,
                    deadline_at=payload.deadline_at,
                    delivery_sent=payload.status == WorkStatus.DELIVERED,
                    delivery_sent_at=datetime.now(timezone.utc) if payload.status == WorkStatus.DELIVERED else None,
                    base_price_for_client=base_price,
                    price_adjustment_percent=adjustment_percent,
                    price_for_client=price_for_client,
                    cost_price=cost_price,
                    margin=margin,
                    additional_expenses=payload.additional_expenses,
                    labor_hours=payload.labor_hours,
                    labor_cost=labor_cost,
                    amount_paid=payload.amount_paid,
                )
            )

            work_items: list[WorkItem] = []
            for item in resolved_work_items_data:
                work_item = await uow.works.add_work_item(
                    WorkItem(
                        work_id=work.id,
                        work_catalog_item_id=item["work_catalog_item_id"],
                        work_type=str(item["work_type"]),
                        description=item["description"],
                        quantity=Decimal(str(item["quantity"])),
                        unit_price=Decimal(str(item["unit_price"])),
                        total_price=Decimal(str(item["total_price"])),
                        sort_order=int(item["sort_order"]),
                    )
                )
                work_item.catalog_item = item["catalog_item"]  # type: ignore[assignment]
                work_items.append(work_item)
            work.work_items = work_items

            for item in material_entries:
                item.work_id = work.id
                await uow.works.add_material_usage(item)

            for item in work_operations:
                item.work_id = work.id
                await uow.operations.add_work_operation(item)
                await uow.operations.add_work_operation_log(
                    WorkOperationLog(
                        work_operation_id=item.id,
                        action="created",
                        actor_email=actor_email,
                        details={
                            "status": item.status,
                            "operation_name": item.operation_name,
                            "quantity": str(item.quantity),
                            "unit_labor_cost": str(item.unit_labor_cost),
                            "total_labor_cost": str(item.total_labor_cost),
                        },
                    )
                )

            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="created",
                    actor_email=actor_email,
                    details={
                        "status": work.status,
                        "client_name": client.name,
                        "executor_name": executor.full_name if executor else None,
                        "doctor_id": work.doctor_id,
                        "doctor_name": work.doctor_name,
                        "doctor_phone": work.doctor_phone,
                        "work_catalog_item_id": work.work_catalog_item_id,
                        "work_type": work.work_type,
                        "patient_name": work.patient_name,
                        "patient_age": work.patient_age,
                        "patient_gender": work.patient_gender,
                        "require_color_photo": work.require_color_photo,
                        "face_shape": work.face_shape,
                        "implant_system": work.implant_system,
                        "metal_type": work.metal_type,
                        "shade_color": work.shade_color,
                        "tooth_formula": work.tooth_formula,
                        "tooth_selection": tooth_selection,
                        "work_items_count": len(work_items),
                        "work_item_types": [item.work_type for item in work_items],
                        "operations_count": len(work_operations),
                        "base_price_for_client": str(work.base_price_for_client),
                        "price_adjustment_percent": str(work.price_adjustment_percent),
                        "price_for_client": str(work.price_for_client),
                    },
                )
            )

            await uow.commit()

        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(
                work,
                client_name=client.name,
                executor_name=executor.full_name if executor else None,
                doctor_name=doctor.full_name if doctor else work.doctor_name,
                work_catalog_item_name=catalog_item.name if catalog_item else None,
                work_catalog_item_code=catalog_item.code if catalog_item else None,
                work_catalog_item_category=catalog_item.category if catalog_item else None,
                work_item_types=[item.work_type for item in work_items],
                work_item_codes=[item.catalog_item.code for item in work_items if item.catalog_item and item.catalog_item.code],
                work_item_descriptions=[item.description for item in work_items if item.description],
                operation_names=operation_names,
                material_names=material_names,
            ),
        )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_work(work.id)

    async def update_status(self, work_id: str, payload: WorkUpdateStatus, *, actor_email: str | None = None) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            previous_status = work.status
            work.status = payload.status.value
            if payload.status in {WorkStatus.COMPLETED, WorkStatus.DELIVERED}:
                work.completed_at = payload.completed_at or work.completed_at or datetime.now(timezone.utc)
            if payload.status == WorkStatus.DELIVERED:
                work.delivery_sent = True
                work.delivery_sent_at = work.delivery_sent_at or datetime.now(timezone.utc)
            else:
                work.delivery_sent = False
                work.delivery_sent_at = None

            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="status_changed",
                    actor_email=actor_email,
                    details={
                        "from_status": previous_status,
                        "to_status": work.status,
                        "completed_at": work.completed_at.isoformat() if work.completed_at else None,
                        "closed_at": work.closed_at.isoformat() if work.closed_at else None,
                    },
                )
            )
            await uow.commit()
            client_name = work.client.name
            executor_name = work.executor.full_name if work.executor else None

        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(work, client_name=client_name, executor_name=executor_name),
        )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_work(work_id)

    async def close_work(self, work_id: str, payload: WorkClose, *, actor_email: str | None = None) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            if work.closed_at is not None:
                raise ConflictError("Work is already closed.", code="work_already_closed")

            previous_status = work.status
            now = datetime.now(timezone.utc)
            work.status = payload.status.value
            if payload.status in {WorkStatus.COMPLETED, WorkStatus.DELIVERED}:
                work.completed_at = payload.completed_at or work.completed_at or now
            work.closed_at = now
            if payload.status == WorkStatus.DELIVERED:
                work.delivery_sent = True
                work.delivery_sent_at = work.delivery_sent_at or now

            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="closed",
                    actor_email=actor_email,
                    details={
                        "from_status": previous_status,
                        "to_status": work.status,
                        "closed_at": work.closed_at.isoformat() if work.closed_at else None,
                        "completed_at": work.completed_at.isoformat() if work.completed_at else None,
                        "note": payload.note,
                    },
                )
            )
            await uow.commit()

        await self._cache.invalidate_prefix("dashboard:")
        await self._reindex_work(work_id)
        return await self.get_work(work_id)

    async def reopen_work(self, work_id: str, payload: WorkReopen, *, actor_email: str | None = None) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            if work.closed_at is None:
                raise ConflictError("Work is not closed.", code="work_not_closed")

            previous_status = work.status
            previous_closed_at = work.closed_at
            work.status = payload.status.value
            work.closed_at = None
            work.completed_at = None
            if work.delivery_sent and payload.status != WorkStatus.DELIVERED:
                work.delivery_sent = False
                work.delivery_sent_at = None

            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="reopened",
                    actor_email=actor_email,
                    details={
                        "from_status": previous_status,
                        "to_status": work.status,
                        "previous_closed_at": previous_closed_at.isoformat() if previous_closed_at else None,
                        "note": payload.note,
                    },
                )
            )
            await uow.commit()

        await self._cache.invalidate_prefix("dashboard:")
        await self._reindex_work(work_id)
        return await self.get_work(work_id)

    async def update_operation_status(
        self,
        work_id: str,
        work_operation_id: str,
        payload: WorkOperationStatusUpdate,
        *,
        actor_email: str | None = None,
    ) -> WorkRead:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)

            work_operation = await uow.operations.get_work_operation(work_id, work_operation_id)
            if work_operation is None:
                raise NotFoundError("work_operation", work_operation_id)

            previous_status = work_operation.status
            work_operation.status = payload.status.value

            await uow.operations.add_work_operation_log(
                WorkOperationLog(
                    work_operation_id=work_operation.id,
                    action="status_changed",
                    actor_email=actor_email,
                    details={
                        "operation_name": work_operation.operation_name,
                        "from_status": previous_status,
                        "to_status": work_operation.status,
                    },
                )
            )
            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="operation_status_changed",
                    actor_email=actor_email,
                    details={
                        "operation_name": work_operation.operation_name,
                        "from_status": previous_status,
                        "to_status": work_operation.status,
                    },
                )
            )
            await uow.commit()
            client_name = work.client.name
            executor_name = work.executor.full_name if work.executor else None

        await self._search.index_document(
            settings.elasticsearch_works_index,
            work.id,
            build_work_search_document(work, client_name=client_name, executor_name=executor_name),
        )
        return await self.get_work(work_id)

    async def get_payroll_summary(
        self,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
        executor_id: str | None = None,
    ) -> WorkPayrollSummaryRead:
        async with self._uow as uow:
            rows = await uow.works.get_executor_payroll_summary(
                date_from=date_from,
                date_to=date_to,
                executor_id=executor_id,
            )

        items = [
            ExecutorPayrollItemRead(
                executor_id=row_executor_id,
                executor_name=executor_name,
                work_count=work_count,
                earnings_total=earnings_total,
                revenue_total=revenue_total,
                closed_from=date_from,
                closed_to=date_to,
            )
            for row_executor_id, executor_name, work_count, earnings_total, revenue_total in rows
        ]
        return WorkPayrollSummaryRead(
            items=items,
            total_earnings=sum((item.earnings_total for item in items), Decimal("0.00")),
            total_revenue=sum((item.revenue_total for item in items), Decimal("0.00")),
        )

    async def upload_attachment(
        self,
        work_id: str,
        *,
        file: UploadFile,
        actor_email: str | None = None,
    ) -> WorkAttachmentRead:
        stored_file = await self._attachments.save(work_id=work_id, file=file)

        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                self._attachments.delete(str(stored_file["storage_key"]))
                raise NotFoundError("work", work_id)

            attachment = await uow.works.add_attachment(
                WorkAttachment(
                    work_id=work.id,
                    file_name=str(stored_file["file_name"]),
                    storage_key=str(stored_file["storage_key"]),
                    content_type=str(stored_file["content_type"]),
                    file_size=int(stored_file["file_size"]),
                    uploaded_by_email=actor_email,
                )
            )
            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="attachment_uploaded",
                    actor_email=actor_email,
                    details={
                        "file_name": attachment.file_name,
                        "content_type": attachment.content_type,
                        "file_size": attachment.file_size,
                    },
                )
            )
            await uow.commit()

        await self._cache.invalidate_prefix("dashboard:")
        await self._reindex_work(work_id)
        return self._map_attachment(work_id, attachment)

    async def delete_attachment(self, work_id: str, attachment_id: str, *, actor_email: str | None = None) -> None:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)

            attachment = await uow.works.get_attachment(work_id, attachment_id)
            if attachment is None:
                raise NotFoundError("work_attachment", attachment_id)

            file_name = attachment.file_name
            storage_key = attachment.storage_key
            await uow.session.delete(attachment)
            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work.id,
                    action="attachment_deleted",
                    actor_email=actor_email,
                    details={"file_name": file_name},
                )
            )
            await uow.commit()

        self._attachments.delete(storage_key)
        await self._cache.invalidate_prefix("dashboard:")
        await self._reindex_work(work_id)

    async def download_attachment(self, work_id: str, attachment_id: str) -> FileResponse:
        async with self._uow as uow:
            attachment = await uow.works.get_attachment(work_id, attachment_id)
            if attachment is None:
                raise NotFoundError("work_attachment", attachment_id)

        return self._attachments.build_file_response(
            storage_key=attachment.storage_key,
            download_name=attachment.file_name,
            media_type=attachment.content_type,
        )

    def _map_work_detail(self, work: Work) -> WorkRead:
        work_items = [
            WorkItemRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                work_catalog_item_id=item.work_catalog_item_id,
                work_catalog_item_code=item.catalog_item.code if item.catalog_item else None,
                work_catalog_item_name=item.catalog_item.name if item.catalog_item else None,
                work_catalog_item_category=item.catalog_item.category if item.catalog_item else None,
                work_type=item.work_type,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                sort_order=item.sort_order,
            )
            for item in sorted(work.work_items, key=lambda entry: entry.sort_order)
        ]
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
        operations = [
            WorkOperationRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                operation_id=item.operation_id,
                operation_code=item.operation_code,
                operation_name=item.operation_name,
                executor_id=item.executor_id,
                executor_name=item.executor.full_name if item.executor else None,
                executor_category_id=item.executor_category_id,
                executor_category_name=item.executor_category.name if item.executor_category else None,
                quantity=item.quantity,
                unit_labor_cost=item.unit_labor_cost,
                total_labor_cost=item.total_labor_cost,
                status=item.status,
                sort_order=item.sort_order,
                manual_rate_override=item.manual_rate_override,
                note=item.note,
                logs=[
                    WorkOperationLogRead(
                        id=log.id,
                        created_at=log.created_at,
                        updated_at=log.updated_at,
                        action=log.action,
                        actor_email=log.actor_email,
                        details=log.details or {},
                    )
                    for log in item.logs
                ],
            )
            for item in sorted(work.work_operations, key=lambda entry: entry.sort_order)
        ]
        change_logs = [
            WorkChangeLogRead(
                id=log.id,
                created_at=log.created_at,
                updated_at=log.updated_at,
                action=log.action,
                actor_email=log.actor_email,
                details=log.details or {},
            )
            for log in work.change_logs
        ]
        attachments = [self._map_attachment(work.id, item) for item in work.attachments]
        return WorkRead(
            id=work.id,
            created_at=work.created_at,
            updated_at=work.updated_at,
            order_number=work.order_number,
            work_type=work.work_type,
            doctor_id=work.doctor_id,
            work_catalog_item_id=work.work_catalog_item_id,
            doctor_name=work.doctor_name,
            doctor_phone=work.doctor_phone,
            patient_name=work.patient_name,
            patient_age=work.patient_age,
            patient_gender=work.patient_gender,
            require_color_photo=work.require_color_photo,
            face_shape=work.face_shape,
            implant_system=work.implant_system,
            metal_type=work.metal_type,
            shade_color=work.shade_color,
            status=work.status,
            received_at=work.received_at,
            deadline_at=work.deadline_at,
            delivery_sent=work.delivery_sent,
            delivery_sent_at=work.delivery_sent_at,
            is_closed=work.closed_at is not None,
            price_for_client=work.price_for_client,
            cost_price=work.cost_price,
            margin=work.margin,
            client_id=work.client_id,
            client_name=work.client.name,
            executor_id=work.executor_id,
            executor_name=work.executor.full_name if work.executor else None,
            work_catalog_item_code=work.catalog_item.code if work.catalog_item else None,
            work_catalog_item_name=work.catalog_item.name if work.catalog_item else None,
            work_catalog_item_category=work.catalog_item.category if work.catalog_item else None,
            description=work.description,
            tooth_formula=work.tooth_formula,
            tooth_selection=work.tooth_selection or [],
            completed_at=work.completed_at,
            closed_at=work.closed_at,
            base_price_for_client=work.base_price_for_client,
            price_adjustment_percent=work.price_adjustment_percent,
            additional_expenses=work.additional_expenses,
            labor_hours=work.labor_hours,
            labor_cost=work.labor_cost,
            amount_paid=work.amount_paid,
            balance_due=max(work.price_for_client - work.amount_paid, Decimal("0.00")),
            work_items=work_items,
            attachments=attachments,
            operations=operations,
            materials=materials,
            change_logs=change_logs,
        )

    def _map_attachment(self, work_id: str, attachment: WorkAttachment) -> WorkAttachmentRead:
        return WorkAttachmentRead(
            id=attachment.id,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
            file_name=attachment.file_name,
            content_type=attachment.content_type,
            file_size=attachment.file_size,
            uploaded_by_email=attachment.uploaded_by_email,
            download_url=self._attachments.build_download_url(work_id, attachment.id, attachment.storage_key),
        )

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
                client_name=work.client.name,
                executor_name=work.executor.full_name if work.executor else None,
                doctor_name=work.doctor.full_name if work.doctor else work.doctor_name,
                work_catalog_item_name=work.catalog_item.name if work.catalog_item else None,
                work_catalog_item_code=work.catalog_item.code if work.catalog_item else None,
                work_catalog_item_category=work.catalog_item.category if work.catalog_item else None,
                work_item_types=[item.work_type for item in work.work_items if item.work_type],
                work_item_codes=[item.catalog_item.code for item in work.work_items if item.catalog_item and item.catalog_item.code],
                work_item_descriptions=[item.description for item in work.work_items if item.description],
                operation_names=[item.operation_name for item in work.work_operations if item.operation_name],
                material_names=[item.material.name for item in work.materials if item.material and item.material.name],
                attachment_names=[item.file_name for item in work.attachments if item.file_name],
            ),
        )

    @staticmethod
    def _resolve_adjustment_percent(
        value: Decimal | None,
        client_default_value: Decimal | None,
    ) -> Decimal:
        if value is not None:
            return value.quantize(TWO_PLACES)
        if client_default_value is not None:
            return client_default_value.quantize(TWO_PLACES)
        return Decimal("0.00")

    @staticmethod
    def _calculate_price(base_price: Decimal, adjustment_percent: Decimal) -> Decimal:
        multiplier = Decimal("1.00") + (adjustment_percent / Decimal("100.00"))
        return (base_price * multiplier).quantize(TWO_PLACES)
