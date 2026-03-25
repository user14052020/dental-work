from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.common.enums import PaymentMethod, WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.narad import Narad
from app.db.models.payment import Payment, PaymentAllocation
from app.db.models.work import Work, WorkChangeLog
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.payments.schemas import (
    PaymentAllocationRead,
    PaymentAllocationUpsert,
    PaymentCompactRead,
    PaymentCreate,
    PaymentListResponse,
    PaymentNaradAllocationRead,
    PaymentNaradAllocationUpsert,
    PaymentRead,
    PaymentReturnNaradAllocation,
    PaymentUpdate,
    NaradPaymentCandidateRead,
    WorkPaymentCandidateRead,
)


TWO_PLACES = Decimal("0.01")


class PaymentService:
    def __init__(
        self,
        uow: SQLAlchemyUnitOfWork,
        cache: CacheService,
        search: SearchService,
    ):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_payments(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        client_id: str | None,
        method: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> PaymentListResponse:
        async with self._uow as uow:
            payments, total_items = await uow.payments.list(
                page=page,
                page_size=page_size,
                search=search,
                client_id=client_id,
                method=method,
                date_from=date_from,
                date_to=date_to,
            )
            items = [self._map_payment(payment) for payment in payments]
        return PaginatedResponse[PaymentCompactRead].create(
            items,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    async def get_payment(self, payment_id: str) -> PaymentRead:
        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            if payment is None:
                raise NotFoundError("payment", payment_id)
            return self._map_payment_detail(payment)

    async def list_work_candidates(
        self,
        client_id: str,
        *,
        payment_id: str | None = None,
    ) -> list[WorkPaymentCandidateRead]:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)

            current_payment = None
            current_allocations: dict[str, Decimal] = {}
            if payment_id:
                current_payment = await uow.payments.get(payment_id)
                if current_payment is None:
                    raise NotFoundError("payment", payment_id)
                if current_payment.client_id != client_id:
                    raise ConflictError(
                        "Payment belongs to a different client.",
                        code="payment_client_mismatch",
                    )
                current_allocations = {
                    allocation.work_id: allocation.amount for allocation in current_payment.allocations
                }

            works = await uow.works.list_by_client(client_id)
            items: list[WorkPaymentCandidateRead] = []
            for work in sorted(works, key=lambda item: item.received_at, reverse=True):
                if work.status == WorkStatus.CANCELLED.value:
                    continue
                existing_amount = current_allocations.get(work.id, Decimal("0.00"))
                balance_without_current_payment = max(
                    work.price_for_client - (work.amount_paid - existing_amount),
                    Decimal("0.00"),
                )
                if balance_without_current_payment <= 0 and existing_amount <= 0:
                    continue
                items.append(
                    WorkPaymentCandidateRead(
                        work_id=work.id,
                        order_number=work.order_number,
                        work_type=work.work_type,
                        status=work.status,
                        received_at=work.received_at,
                        deadline_at=work.deadline_at,
                        total_price=work.price_for_client,
                        amount_paid=work.amount_paid,
                        balance_due=max(work.price_for_client - work.amount_paid, Decimal("0.00")),
                        available_to_allocate=balance_without_current_payment.quantize(TWO_PLACES),
                        existing_allocation_amount=existing_amount.quantize(TWO_PLACES),
                    )
                )
            return items

    async def list_narad_candidates(
        self,
        client_id: str,
        *,
        payment_id: str | None = None,
    ) -> list[NaradPaymentCandidateRead]:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)

            current_allocations: dict[str, Decimal] = {}
            if payment_id:
                current_payment = await uow.payments.get(payment_id)
                if current_payment is None:
                    raise NotFoundError("payment", payment_id)
                if current_payment.client_id != client_id:
                    raise ConflictError(
                        "Payment belongs to a different client.",
                        code="payment_client_mismatch",
                    )
                current_allocations = {
                    allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                    for allocation in current_payment.allocations
                }

            works = await uow.works.list_by_client(client_id)
            grouped = self._group_works_by_narad(works)
            items: list[NaradPaymentCandidateRead] = []
            for group in sorted(
                grouped.values(),
                key=lambda item: item["narad"].received_at,
                reverse=True,
            ):
                narad = group["narad"]
                narad_works = group["works"]
                existing_amount = sum(
                    (current_allocations.get(work.id, Decimal("0.00")) for work in narad_works),
                    start=Decimal("0.00"),
                ).quantize(TWO_PLACES)
                total_price = sum((work.price_for_client for work in narad_works), start=Decimal("0.00")).quantize(
                    TWO_PLACES
                )
                amount_paid = sum((work.amount_paid for work in narad_works), start=Decimal("0.00")).quantize(
                    TWO_PLACES
                )
                balance_due = max(total_price - amount_paid, Decimal("0.00")).quantize(TWO_PLACES)
                balance_without_current_payment = max(
                    total_price - (amount_paid - existing_amount),
                    Decimal("0.00"),
                ).quantize(TWO_PLACES)
                if balance_without_current_payment <= 0 and existing_amount <= 0:
                    continue
                items.append(
                    NaradPaymentCandidateRead(
                        narad_id=narad.id,
                        narad_number=narad.narad_number,
                        title=narad.title,
                        status=narad.status,
                        received_at=narad.received_at,
                        deadline_at=narad.deadline_at,
                        works_count=len(narad_works),
                        total_price=total_price,
                        amount_paid=amount_paid,
                        balance_due=balance_due,
                        available_to_allocate=balance_without_current_payment,
                        existing_allocation_amount=existing_amount,
                    )
                )
            return items

    async def create_payment(self, payload: PaymentCreate, *, actor_email: str | None = None) -> PaymentRead:
        async with self._uow as uow:
            client = await uow.clients.get(payload.client_id)
            if client is None:
                raise NotFoundError("client", payload.client_id)

            payment_number = await self._resolve_payment_number(
                uow,
                payload.payment_number,
                payload.payment_date,
            )
            resolved_allocations = await self._resolve_allocations(
                uow,
                client_id=payload.client_id,
                allocations=payload.allocations,
                narad_allocations=payload.narad_allocations,
            )
            _, _, total_allocated = await self._validate_allocations(
                uow,
                client_id=payload.client_id,
                payment_amount=payload.amount,
                allocations=resolved_allocations,
            )

            payment = await uow.payments.add(
                Payment(
                    payment_number=payment_number,
                    client_id=payload.client_id,
                    payment_date=payload.payment_date,
                    method=payload.method.value if isinstance(payload.method, PaymentMethod) else str(payload.method),
                    amount=payload.amount.quantize(TWO_PLACES),
                    external_reference=payload.external_reference,
                    comment=payload.comment,
                )
            )
            payment.allocations = [
                PaymentAllocation(
                    work_id=item.work_id,
                    amount=item.amount.quantize(TWO_PLACES),
                )
                for item in resolved_allocations
            ]

            affected_work_ids = {item.work_id for item in resolved_allocations}
            await uow.payments.flush()
            await self._sync_work_amount_paid(uow, affected_work_ids)
            await self._log_allocation_changes(
                uow,
                payment_id=payment.id,
                payment_number=payment.payment_number,
                old_allocations={},
                new_allocations={item.work_id: item.amount.quantize(TWO_PLACES) for item in resolved_allocations},
                actor_email=actor_email,
            )
            await uow.commit()

            payment = await uow.payments.get(payment.id)
            if payment is None:
                raise NotFoundError("payment", payment.id)

        await self._after_payment_changed(affected_work_ids)
        return self._map_payment_detail(payment, allocated_total_override=total_allocated)

    async def update_payment(
        self,
        payment_id: str,
        payload: PaymentUpdate,
        *,
        actor_email: str | None = None,
    ) -> PaymentRead:
        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

            target_client_id = payload.client_id or payment.client_id
            client = await uow.clients.get(target_client_id)
            if client is None:
                raise NotFoundError("client", target_client_id)

            target_payment_number = await self._resolve_payment_number(
                uow,
                payload.payment_number if payload.payment_number is not None else payment.payment_number,
                payload.payment_date or payment.payment_date,
                current_payment_id=payment.id,
            )
            target_payment_date = payload.payment_date or payment.payment_date
            target_method = (
                payload.method.value
                if isinstance(payload.method, PaymentMethod)
                else payload.method or payment.method
            )
            target_amount = (payload.amount or payment.amount).quantize(TWO_PLACES)
            target_external_reference = (
                payload.external_reference if payload.external_reference is not None else payment.external_reference
            )
            target_comment = payload.comment if payload.comment is not None else payment.comment

            old_allocations = {
                allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                for allocation in payment.allocations
            }
            target_allocations = await self._resolve_allocations(
                uow,
                client_id=target_client_id,
                allocations=payload.allocations,
                narad_allocations=payload.narad_allocations,
                fallback_allocations=[
                    PaymentAllocationUpsert(work_id=allocation.work_id, amount=allocation.amount)
                    for allocation in payment.allocations
                ],
                exclude_payment_id=payment.id,
            )

            _, _, total_allocated = await self._validate_allocations(
                uow,
                client_id=target_client_id,
                payment_amount=target_amount,
                allocations=target_allocations,
                exclude_payment_id=payment.id,
            )

            payment.payment_number = target_payment_number
            payment.client_id = target_client_id
            payment.payment_date = target_payment_date
            payment.method = target_method
            payment.amount = target_amount
            payment.external_reference = target_external_reference
            payment.comment = target_comment
            payment.allocations = [
                PaymentAllocation(
                    work_id=item.work_id,
                    amount=item.amount.quantize(TWO_PLACES),
                )
                for item in target_allocations
            ]

            new_allocations = {
                item.work_id: item.amount.quantize(TWO_PLACES) for item in target_allocations
            }
            affected_work_ids = set(old_allocations) | set(new_allocations)
            await uow.payments.flush()
            await self._sync_work_amount_paid(uow, affected_work_ids)
            await self._log_allocation_changes(
                uow,
                payment_id=payment.id,
                payment_number=payment.payment_number,
                old_allocations=old_allocations,
                new_allocations=new_allocations,
                actor_email=actor_email,
            )
            await uow.commit()

            payment = await uow.payments.get(payment.id)
            if payment is None:
                raise NotFoundError("payment", payment.id)

        await self._after_payment_changed(affected_work_ids)
        return self._map_payment_detail(payment, allocated_total_override=total_allocated)

    async def delete_payment(self, payment_id: str, *, actor_email: str | None = None) -> None:
        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

            old_allocations = {
                allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                for allocation in payment.allocations
            }
            affected_work_ids = set(old_allocations)
            await self._log_allocation_changes(
                uow,
                payment_id=payment.id,
                payment_number=payment.payment_number,
                old_allocations=old_allocations,
                new_allocations={},
                actor_email=actor_email,
            )
            await uow.payments.delete(payment)
            await uow.payments.flush()
            await self._sync_work_amount_paid(uow, affected_work_ids)
            await uow.commit()

        await self._after_payment_changed(affected_work_ids)

    async def return_narad_allocation(
        self,
        payment_id: str,
        payload: PaymentReturnNaradAllocation,
        *,
        actor_email: str | None = None,
    ) -> PaymentRead:
        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

            old_allocations = {
                allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                for allocation in payment.allocations
            }
            target_work_ids = {
                allocation.work_id
                for allocation in payment.allocations
                if allocation.work and allocation.work.narad_id == payload.narad_id
            }
            if not target_work_ids:
                raise NotFoundError("payment_narad_allocation", f"{payment_id}:{payload.narad_id}")

            payment.allocations = [
                allocation for allocation in payment.allocations if allocation.work_id not in target_work_ids
            ]
            new_allocations = {
                allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                for allocation in payment.allocations
            }

            await uow.payments.flush()
            await self._sync_work_amount_paid(uow, target_work_ids)
            await self._log_allocation_changes(
                uow,
                payment_id=payment.id,
                payment_number=payment.payment_number,
                old_allocations=old_allocations,
                new_allocations=new_allocations,
                actor_email=actor_email,
            )
            await uow.commit()

            payment = await uow.payments.get(payment.id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

        await self._after_payment_changed(target_work_ids)
        return self._map_payment_detail(payment)

    async def delete_unallocated_balance(
        self,
        payment_id: str,
        *,
        actor_email: str | None = None,
    ) -> PaymentRead:
        async with self._uow as uow:
            payment = await uow.payments.get(payment_id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

            allocated_total = sum((allocation.amount for allocation in payment.allocations), Decimal("0.00")).quantize(
                TWO_PLACES
            )
            unallocated_total = max(payment.amount - allocated_total, Decimal("0.00")).quantize(TWO_PLACES)
            if unallocated_total <= 0:
                raise ConflictError(
                    "Payment has no unallocated remainder to delete.",
                    code="payment_no_unallocated_remainder",
                )

            payment.amount = allocated_total
            await uow.payments.flush()
            await uow.commit()

            payment = await uow.payments.get(payment.id)
            if payment is None:
                raise NotFoundError("payment", payment_id)

        await self._cache.invalidate_prefix("dashboard:")
        return self._map_payment_detail(payment)

    async def _resolve_payment_number(
        self,
        uow: SQLAlchemyUnitOfWork,
        payment_number: str | None,
        payment_date: datetime,
        *,
        current_payment_id: str | None = None,
    ) -> str:
        if payment_number:
            existing = await uow.payments.get_by_number(payment_number)
            if existing is not None and existing.id != current_payment_id:
                raise ConflictError(
                    "Payment number already exists.",
                    code="payment_number_exists",
                )
            return payment_number

        base_prefix = f"PAY-{payment_date.strftime('%Y%m%d')}"
        index = 1
        while True:
            candidate = f"{base_prefix}-{index:03d}"
            existing = await uow.payments.get_by_number(candidate)
            if existing is None or existing.id == current_payment_id:
                return candidate
            index += 1

    async def _resolve_allocations(
        self,
        uow: SQLAlchemyUnitOfWork,
        *,
        client_id: str,
        allocations: list[PaymentAllocationUpsert] | None,
        narad_allocations: list[PaymentNaradAllocationUpsert] | None,
        fallback_allocations: list[PaymentAllocationUpsert] | None = None,
        exclude_payment_id: str | None = None,
    ) -> list[PaymentAllocationUpsert]:
        if narad_allocations is not None:
            return await self._expand_narad_allocations(
                uow,
                client_id=client_id,
                narad_allocations=narad_allocations,
                exclude_payment_id=exclude_payment_id,
            )
        if allocations is not None:
            return allocations
        return fallback_allocations or []

    async def _expand_narad_allocations(
        self,
        uow: SQLAlchemyUnitOfWork,
        *,
        client_id: str,
        narad_allocations: list[PaymentNaradAllocationUpsert],
        exclude_payment_id: str | None = None,
    ) -> list[PaymentAllocationUpsert]:
        if not narad_allocations:
            return []

        works = await uow.works.list_by_client(client_id)
        grouped = self._group_works_by_narad(works)
        current_payment_allocations: dict[str, Decimal] = {}
        if exclude_payment_id:
            current_payment = await uow.payments.get(exclude_payment_id)
            if current_payment is None:
                raise NotFoundError("payment", exclude_payment_id)
            current_payment_allocations = {
                allocation.work_id: allocation.amount.quantize(TWO_PLACES)
                for allocation in current_payment.allocations
            }

        allocations_by_work: dict[str, Decimal] = {}
        seen_narad_ids: set[str] = set()
        for narad_allocation in narad_allocations:
            if narad_allocation.narad_id in seen_narad_ids:
                raise ConflictError(
                    "Each narad can be allocated only once in a single payment.",
                    code="payment_allocation_duplicate_narad",
                )
            seen_narad_ids.add(narad_allocation.narad_id)

            group = grouped.get(narad_allocation.narad_id)
            if group is None:
                narad = await uow.narads.get(narad_allocation.narad_id)
                if narad is None:
                    raise NotFoundError("narad", narad_allocation.narad_id)
                if narad.client_id != client_id:
                    raise ConflictError(
                        "Payment allocation must reference narads of the same client.",
                        code="payment_allocation_client_mismatch",
                        details={"narad_id": narad_allocation.narad_id},
                    )
                raise ConflictError(
                    "Narad has no active works available for payment allocation.",
                    code="payment_allocation_empty_narad",
                    details={"narad_id": narad_allocation.narad_id},
                )

            narad_works = group["works"]
            remaining = narad_allocation.amount.quantize(TWO_PLACES)
            for work in narad_works:
                current_payment_amount = current_payment_allocations.get(work.id, Decimal("0.00"))
                available = max(
                    work.price_for_client - (work.amount_paid - current_payment_amount),
                    Decimal("0.00"),
                ).quantize(TWO_PLACES)
                if available <= 0:
                    continue
                chunk = min(remaining, available)
                if chunk <= 0:
                    continue
                allocations_by_work[work.id] = allocations_by_work.get(work.id, Decimal("0.00")) + chunk
                remaining = (remaining - chunk).quantize(TWO_PLACES)
                if remaining <= 0:
                    break

            if remaining > 0:
                narad = group["narad"]
                raise ConflictError(
                    "Allocation exceeds remaining balance of the narad.",
                    code="payment_allocation_exceeds_narad_balance",
                    details={
                        "narad_id": narad.id,
                        "narad_number": narad.narad_number,
                        "requested_amount": narad_allocation.amount.quantize(TWO_PLACES),
                        "available_amount": (
                            narad_allocation.amount.quantize(TWO_PLACES) - remaining
                        ).quantize(TWO_PLACES),
                    },
                )

        return [
            PaymentAllocationUpsert(work_id=work_id, amount=amount.quantize(TWO_PLACES))
            for work_id, amount in allocations_by_work.items()
            if amount > 0
        ]

    @staticmethod
    def _group_works_by_narad(works: list[Work]) -> dict[str, dict[str, Narad | list[Work]]]:
        grouped: dict[str, dict[str, Narad | list[Work]]] = {}
        for work in works:
            if work.status == WorkStatus.CANCELLED.value or work.narad is None:
                continue
            group = grouped.setdefault(work.narad_id, {"narad": work.narad, "works": []})
            group["works"].append(work)  # type: ignore[index]

        for group in grouped.values():
            group["works"] = sorted(  # type: ignore[index]
                group["works"],  # type: ignore[index]
                key=lambda item: (item.received_at, item.created_at, item.id),
            )
        return grouped

    async def _validate_allocations(
        self,
        uow: SQLAlchemyUnitOfWork,
        *,
        client_id: str,
        payment_amount: Decimal,
        allocations: list[PaymentAllocationUpsert],
        exclude_payment_id: str | None = None,
    ) -> tuple[dict[str, Work], dict[str, Decimal], Decimal]:
        work_map: dict[str, Work] = {}
        allocation_map: dict[str, Decimal] = {}
        total_allocated = Decimal("0.00")

        for allocation in allocations:
            if allocation.work_id in allocation_map:
                raise ConflictError(
                    "Each work can be allocated only once in a single payment.",
                    code="payment_allocation_duplicate_work",
                )
            work = await uow.works.get(allocation.work_id)
            if work is None:
                raise NotFoundError("work", allocation.work_id)
            if work.client_id != client_id:
                raise ConflictError(
                    "Payment allocation must reference works of the same client.",
                    code="payment_allocation_client_mismatch",
                    details={"work_id": allocation.work_id},
                )
            if work.status == WorkStatus.CANCELLED.value:
                raise ConflictError(
                    "Cancelled work cannot receive payments.",
                    code="payment_allocation_cancelled_work",
                    details={"work_id": allocation.work_id},
                )

            other_paid_total = await uow.payments.sum_allocated_to_work(
                allocation.work_id,
                exclude_payment_id=exclude_payment_id,
            )
            allowed_amount = max(work.price_for_client - other_paid_total, Decimal("0.00")).quantize(TWO_PLACES)
            target_amount = allocation.amount.quantize(TWO_PLACES)
            if target_amount > allowed_amount:
                raise ConflictError(
                    "Allocation exceeds remaining balance of the work.",
                    code="payment_allocation_exceeds_work_balance",
                    details={
                        "work_id": allocation.work_id,
                        "allowed_amount": allowed_amount,
                        "requested_amount": target_amount,
                    },
                )

            work_map[allocation.work_id] = work
            allocation_map[allocation.work_id] = target_amount
            total_allocated += target_amount

        total_allocated = total_allocated.quantize(TWO_PLACES)
        if total_allocated > payment_amount.quantize(TWO_PLACES):
            raise ConflictError(
                "Allocated amount exceeds payment amount.",
                code="payment_overallocated",
                details={
                    "payment_amount": payment_amount.quantize(TWO_PLACES),
                    "allocated_total": total_allocated,
                },
            )
        return work_map, allocation_map, total_allocated

    async def _sync_work_amount_paid(self, uow: SQLAlchemyUnitOfWork, work_ids: set[str]) -> None:
        if not work_ids:
            return

        works = await uow.works.list_by_ids(list(work_ids))
        allocation_totals = await uow.payments.sum_allocations_by_work_ids(list(work_ids))
        for work in works:
            work.amount_paid = allocation_totals.get(work.id, Decimal("0.00")).quantize(TWO_PLACES)

    async def _log_allocation_changes(
        self,
        uow: SQLAlchemyUnitOfWork,
        *,
        payment_id: str,
        payment_number: str,
        old_allocations: dict[str, Decimal],
        new_allocations: dict[str, Decimal],
        actor_email: str | None,
    ) -> None:
        affected_work_ids = set(old_allocations) | set(new_allocations)
        for work_id in affected_work_ids:
            previous_amount = old_allocations.get(work_id, Decimal("0.00")).quantize(TWO_PLACES)
            current_amount = new_allocations.get(work_id, Decimal("0.00")).quantize(TWO_PLACES)
            if previous_amount == current_amount:
                continue

            if previous_amount == 0 and current_amount > 0:
                action = "payment_allocation_added"
            elif previous_amount > 0 and current_amount == 0:
                action = "payment_allocation_removed"
            else:
                action = "payment_allocation_updated"

            await uow.works.add_change_log(
                WorkChangeLog(
                    work_id=work_id,
                    action=action,
                    actor_email=actor_email,
                    details={
                        "payment_id": payment_id,
                        "payment_number": payment_number,
                        "previous_amount": previous_amount,
                        "current_amount": current_amount,
                    },
                )
            )

    async def _after_payment_changed(self, affected_work_ids: set[str]) -> None:
        for work_id in affected_work_ids:
            await self._reindex_work(work_id)
        await self._cache.invalidate_prefix("dashboard:")

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
                doctor_name=work.narad.doctor_name if work.narad else None,
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

    def _map_payment(self, payment: Payment) -> PaymentCompactRead:
        allocated_total = sum((allocation.amount for allocation in payment.allocations), Decimal("0.00")).quantize(TWO_PLACES)
        return PaymentCompactRead(
            id=payment.id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            payment_number=payment.payment_number,
            client_id=payment.client_id,
            client_name=payment.client.name if payment.client else "—",
            payment_date=payment.payment_date,
            method=payment.method,
            amount=payment.amount,
            allocated_total=allocated_total,
            unallocated_total=max(payment.amount - allocated_total, Decimal("0.00")).quantize(TWO_PLACES),
            allocation_count=len(payment.allocations),
            external_reference=payment.external_reference,
            comment=payment.comment,
        )

    def _map_payment_detail(
        self,
        payment: Payment,
        *,
        allocated_total_override: Decimal | None = None,
    ) -> PaymentRead:
        compact = self._map_payment(payment)
        allocated_total = compact.allocated_total if allocated_total_override is None else allocated_total_override
        allocations = [
            PaymentAllocationRead(
                id=allocation.id,
                created_at=allocation.created_at,
                updated_at=allocation.updated_at,
                work_id=allocation.work_id,
                narad_id=allocation.work.narad_id if allocation.work else None,
                narad_number=allocation.work.narad.narad_number if allocation.work and allocation.work.narad else None,
                narad_title=allocation.work.narad.title if allocation.work and allocation.work.narad else None,
                work_order_number=allocation.work.order_number if allocation.work else "—",
                work_type=allocation.work.work_type if allocation.work else "—",
                work_status=allocation.work.status if allocation.work else WorkStatus.NEW.value,
                received_at=allocation.work.received_at if allocation.work else payment.payment_date,
                deadline_at=allocation.work.deadline_at if allocation.work else None,
                work_total=allocation.work.price_for_client if allocation.work else Decimal("0.00"),
                work_amount_paid=allocation.work.amount_paid if allocation.work else allocation.amount,
                work_balance_due=(
                    max(allocation.work.price_for_client - allocation.work.amount_paid, Decimal("0.00"))
                    if allocation.work
                    else Decimal("0.00")
                ),
                amount=allocation.amount,
            )
            for allocation in payment.allocations
        ]
        narad_allocations = self._build_narad_allocation_reads(payment)
        payload = compact.model_dump(exclude={"allocated_total", "unallocated_total"})
        return PaymentRead(
            **payload,
            allocated_total=allocated_total,
            unallocated_total=max(payment.amount - allocated_total, Decimal("0.00")).quantize(TWO_PLACES),
            allocations=allocations,
            narad_allocations=narad_allocations,
        )

    def _build_narad_allocation_reads(self, payment: Payment) -> list[PaymentNaradAllocationRead]:
        grouped: dict[str, dict[str, object]] = {}
        for allocation in payment.allocations:
            work = allocation.work
            narad = work.narad if work else None
            if work is None or narad is None:
                continue

            group = grouped.setdefault(
                narad.id,
                {
                    "narad": narad,
                    "amount": Decimal("0.00"),
                    "works_count": 0,
                    "seen_work_ids": set(),
                },
            )
            group["amount"] = (group["amount"] + allocation.amount).quantize(TWO_PLACES)  # type: ignore[index]
            seen_work_ids = group["seen_work_ids"]  # type: ignore[assignment]
            if work.id not in seen_work_ids:
                seen_work_ids.add(work.id)
                group["works_count"] = len(seen_work_ids)  # type: ignore[index]

        reads: list[PaymentNaradAllocationRead] = []
        for group in grouped.values():
            narad = group["narad"]  # type: ignore[assignment]
            amount = group["amount"]  # type: ignore[assignment]
            total_price = sum((work.price_for_client for work in narad.works), start=Decimal("0.00")).quantize(TWO_PLACES)
            amount_paid = sum((work.amount_paid for work in narad.works), start=Decimal("0.00")).quantize(TWO_PLACES)
            reads.append(
                PaymentNaradAllocationRead(
                    narad_id=narad.id,
                    narad_number=narad.narad_number,
                    narad_title=narad.title,
                    narad_status=narad.status,
                    received_at=narad.received_at,
                    deadline_at=narad.deadline_at,
                    works_count=int(group["works_count"]),  # type: ignore[arg-type]
                    total_price=total_price,
                    amount_paid=amount_paid,
                    balance_due=max(total_price - amount_paid, Decimal("0.00")).quantize(TWO_PLACES),
                    amount=amount,
                )
            )

        return sorted(reads, key=lambda item: (item.received_at, item.narad_number), reverse=True)
