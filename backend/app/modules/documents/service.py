from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from app.common.vat import calculate_vat_breakdown
from app.core.exceptions import NotFoundError
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.documents.templates import (
    build_work_line_items,
    render_act_html,
    render_invoice_html,
    render_job_order_html,
)


class DocumentService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def render_invoice(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_invoice_html(context)

    async def render_act(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_act_html(context)

    async def render_job_order(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_job_order_html(context)

    async def _build_context(self, work_id: str) -> dict[str, object]:
        async with self._uow as uow:
            work = await uow.works.get(work_id)
            if work is None:
                raise NotFoundError("work", work_id)
            organization = await uow.organization.get_profile()
            if organization is None:
                raise NotFoundError("organization_profile", "default")

            line_items = build_work_line_items(work)
            total = sum((item["total"] for item in line_items), start=Decimal("0.00"))
            vat_breakdown = calculate_vat_breakdown(
                total,
                getattr(organization, "vat_mode", None),
                getattr(organization, "vat_label", None),
            )
            document_date = work.closed_at or work.completed_at or work.received_at
            if hasattr(document_date, "astimezone"):
                document_date = document_date.astimezone(timezone.utc)

            return {
                "organization": organization,
                "client": work.client,
                "work": work,
                "line_items": line_items,
                "total": total,
                "vat": vat_breakdown,
                "document_date": document_date,
            }
