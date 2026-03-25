from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from app.common.email import SmtpEmailSender, SmtpSettings
from app.common.vat import calculate_vat_breakdown
from app.core.exceptions import ConflictError, NotFoundError
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.documents.schemas import DocumentEmailRead
from app.modules.documents.templates import (
    build_client_line_items,
    build_narad_job_order_items,
    build_narad_line_items,
    build_work_line_items,
    render_act_html,
    render_invoice_html,
    render_job_order_html,
)


class DocumentService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, email_sender: SmtpEmailSender | None = None):
        self._uow = uow
        self._email_sender = email_sender or SmtpEmailSender()

    async def render_invoice(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_invoice_html(context)

    async def render_act(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_act_html(context)

    async def render_job_order(self, work_id: str) -> str:
        context = await self._build_context(work_id)
        return render_job_order_html(context)

    async def render_narad_invoice(self, narad_id: str) -> str:
        context = await self._build_narad_context(narad_id)
        return render_invoice_html(context)

    async def render_narad_act(self, narad_id: str) -> str:
        context = await self._build_narad_context(narad_id)
        return render_act_html(context)

    async def render_narad_job_order(self, narad_id: str) -> str:
        context = await self._build_narad_context(narad_id)
        return render_job_order_html(context)

    async def render_client_invoice(
        self,
        client_id: str,
        *,
        date_from,
        date_to,
    ) -> str:
        context = await self._build_client_group_context(client_id, date_from=date_from, date_to=date_to)
        context["document_heading"] = (
            f"Счет по нарядам клиента {context['client'].legal_name or context['client'].name} "
            f"от {context['document_date']:%d.%m.%Y}"
        )
        return render_invoice_html(context)

    async def render_client_act(
        self,
        client_id: str,
        *,
        date_from,
        date_to,
    ) -> str:
        context = await self._build_client_group_context(client_id, date_from=date_from, date_to=date_to)
        context["document_heading"] = (
            f"Акт по нарядам клиента {context['client'].legal_name or context['client'].name} "
            f"от {context['document_date']:%d.%m.%Y}"
        )
        return render_act_html(context)

    async def send_narad_document_email(
        self,
        narad_id: str,
        *,
        kind: str,
        recipient_email: str | None = None,
        subject: str | None = None,
    ) -> DocumentEmailRead:
        context = await self._build_narad_context(narad_id)
        return await self._send_document_email(
            kind=kind,
            context=context,
            recipient_email=recipient_email,
            subject=subject,
        )

    async def send_client_document_email(
        self,
        client_id: str,
        *,
        kind: str,
        recipient_email: str | None = None,
        subject: str | None = None,
        date_from=None,
        date_to=None,
    ) -> DocumentEmailRead:
        context = await self._build_client_group_context(client_id, date_from=date_from, date_to=date_to)
        context["document_heading"] = (
            f"{'Счет' if kind == 'invoice' else 'Акт'} по нарядам клиента "
            f"{context['client'].legal_name or context['client'].name} "
            f"от {context['document_date']:%d.%m.%Y}"
        )
        return await self._send_document_email(
            kind=kind,
            context=context,
            recipient_email=recipient_email,
            subject=subject,
        )

    async def _send_document_email(
        self,
        *,
        kind: str,
        context: dict[str, object],
        recipient_email: str | None,
        subject: str | None,
    ) -> DocumentEmailRead:
        organization = context["organization"]
        client = context["client"]
        resolved_recipient = recipient_email or getattr(client, "email", None)
        if not resolved_recipient:
            raise ConflictError(
                "У клиента не указан e-mail для отправки документа.",
                code="document_email_recipient_required",
            )

        smtp_settings = SmtpSettings(
            host=getattr(organization, "smtp_host", None) or "",
            port=getattr(organization, "smtp_port", 587) or 587,
            username=getattr(organization, "smtp_username", None),
            password=getattr(organization, "smtp_password", None),
            from_email=getattr(organization, "smtp_from_email", None),
            from_name=getattr(organization, "smtp_from_name", None),
            reply_to=getattr(organization, "smtp_reply_to", None),
            use_tls=bool(getattr(organization, "smtp_use_tls", True)),
            use_ssl=bool(getattr(organization, "smtp_use_ssl", False)),
        )
        if not smtp_settings.is_configured:
            raise ConflictError(
                "SMTP-настройки организации не заполнены.",
                code="smtp_not_configured",
            )

        html_body = self._render_document_html(kind, context)
        resolved_subject = subject or self._build_email_subject(kind, context)
        await self._email_sender.send_html(
            settings=smtp_settings,
            recipient_email=resolved_recipient,
            subject=resolved_subject,
            html_body=html_body,
        )
        return DocumentEmailRead(kind=kind, recipient_email=resolved_recipient, subject=resolved_subject)

    @staticmethod
    def _render_document_html(kind: str, context: dict[str, object]) -> str:
        if kind == "invoice":
            return render_invoice_html(context)
        if kind == "act":
            return render_act_html(context)
        if kind == "job-order":
            return render_job_order_html(context)
        raise ConflictError("Неизвестный тип документа для отправки.", code="document_kind_unsupported")

    @staticmethod
    def _build_email_subject(kind: str, context: dict[str, object]) -> str:
        document_titles = {
            "invoice": "Счет",
            "act": "Акт",
            "job-order": "Наряд",
        }
        client = context["client"]
        document_number = context["document_number"]
        return f"{document_titles.get(kind, 'Документ')} № {document_number} для {getattr(client, 'legal_name', None) or client.name}"

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
                "narad": work.narad,
                "primary_work": work,
                "work": work,
                "document_number": work.narad.narad_number if getattr(work, "narad", None) else work.order_number,
                "line_items": line_items,
                "job_order_items": build_narad_job_order_items(work.narad) if getattr(work, "narad", None) else line_items,
                "total": total,
                "vat": vat_breakdown,
                "document_date": document_date,
            }

    async def _build_narad_context(self, narad_id: str) -> dict[str, object]:
        async with self._uow as uow:
            narad = await uow.narads.get(narad_id)
            if narad is None:
                raise NotFoundError("narad", narad_id)
            if not narad.works:
                raise NotFoundError("narad_works", narad_id)

            organization = await uow.organization.get_profile()
            if organization is None:
                raise NotFoundError("organization_profile", "default")

            primary_work = narad.works[0]
            line_items = build_narad_line_items(narad)
            total = sum((item["total"] for item in line_items), start=Decimal("0.00"))
            vat_breakdown = calculate_vat_breakdown(
                total,
                getattr(organization, "vat_mode", None),
                getattr(organization, "vat_label", None),
            )
            document_date = narad.closed_at or narad.completed_at or narad.received_at
            if hasattr(document_date, "astimezone"):
                document_date = document_date.astimezone(timezone.utc)

            return {
                "organization": organization,
                "client": narad.client,
                "narad": narad,
                "primary_work": primary_work,
                "work": primary_work,
                "document_number": narad.narad_number,
                "line_items": line_items,
                "job_order_items": build_narad_job_order_items(narad),
                "total": total,
                "vat": vat_breakdown,
                "document_date": document_date,
            }

    async def _build_client_group_context(self, client_id: str, *, date_from, date_to) -> dict[str, object]:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)

            organization = await uow.organization.get_profile()
            if organization is None:
                raise NotFoundError("organization_profile", "default")

            narads = await uow.narads.list_closed_by_client(client_id, date_from=date_from, date_to=date_to)
            if not narads:
                raise NotFoundError("closed_narads_for_client", client_id)

            primary_narad = narads[0]
            primary_work = primary_narad.works[0]
            line_items = build_client_line_items(narads)
            total = sum((item["total"] for item in line_items), start=Decimal("0.00"))
            vat_breakdown = calculate_vat_breakdown(
                total,
                getattr(organization, "vat_mode", None),
                getattr(organization, "vat_label", None),
            )
            document_date = max((narad.closed_at or narad.completed_at or narad.received_at for narad in narads))
            if hasattr(document_date, "astimezone"):
                document_date = document_date.astimezone(timezone.utc)

            period_start = min((narad.closed_at or narad.completed_at or narad.received_at for narad in narads))
            period_end = document_date
            period_label = f"{period_start:%d.%m.%Y} - {period_end:%d.%m.%Y}" if period_start.date() != period_end.date() else f"{period_end:%d.%m.%Y}"
            narad_numbers = ", ".join(narad.narad_number for narad in narads[:12])
            if len(narads) > 12:
                narad_numbers += f" и еще {len(narads) - 12}"

            return {
                "organization": organization,
                "client": client,
                "narad": primary_narad,
                "primary_work": primary_work,
                "work": primary_work,
                "document_number": f"GROUP-{client.id[:8].upper()}",
                "line_items": line_items,
                "job_order_items": build_narad_job_order_items(primary_narad),
                "total": total,
                "vat": vat_breakdown,
                "document_date": document_date,
                "scope_note": (
                    f"Закрытые наряды за период {period_label}: {narad_numbers}"
                ),
            }
