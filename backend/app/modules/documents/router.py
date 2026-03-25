from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_current_user, get_document_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.documents.schemas import ClientDocumentEmailPayload, DocumentEmailRead, NaradDocumentEmailPayload
from app.modules.documents.service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/works/{work_id}/invoice", response_class=HTMLResponse)
async def render_invoice(
    work_id: str,
    _: UserRead = Depends(require_permissions("works.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_invoice(work_id))


@router.get("/works/{work_id}/act", response_class=HTMLResponse)
async def render_act(
    work_id: str,
    _: UserRead = Depends(require_permissions("works.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_act(work_id))


@router.get("/works/{work_id}/job-order", response_class=HTMLResponse)
async def render_job_order(
    work_id: str,
    _: UserRead = Depends(require_permissions("works.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_job_order(work_id))


@router.get("/narads/{narad_id}/invoice", response_class=HTMLResponse)
async def render_narad_invoice(
    narad_id: str,
    _: UserRead = Depends(require_permissions("narads.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_narad_invoice(narad_id))


@router.get("/narads/{narad_id}/act", response_class=HTMLResponse)
async def render_narad_act(
    narad_id: str,
    _: UserRead = Depends(require_permissions("narads.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_narad_act(narad_id))


@router.get("/narads/{narad_id}/job-order", response_class=HTMLResponse)
async def render_narad_job_order(
    narad_id: str,
    _: UserRead = Depends(require_permissions("narads.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_narad_job_order(narad_id))


@router.get("/clients/{client_id}/invoice", response_class=HTMLResponse)
async def render_client_invoice(
    client_id: str,
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    _: UserRead = Depends(require_permissions("clients.manage", "payments.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_client_invoice(client_id, date_from=date_from, date_to=date_to))


@router.get("/clients/{client_id}/act", response_class=HTMLResponse)
async def render_client_act(
    client_id: str,
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    _: UserRead = Depends(require_permissions("clients.manage", "payments.manage")),
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_client_act(client_id, date_from=date_from, date_to=date_to))


@router.post("/narads/{narad_id}/email", response_model=DocumentEmailRead)
async def send_narad_document_email(
    narad_id: str,
    payload: NaradDocumentEmailPayload,
    _: UserRead = Depends(require_permissions("narads.manage")),
    service: DocumentService = Depends(get_document_service),
) -> DocumentEmailRead:
    return await service.send_narad_document_email(
        narad_id,
        kind=payload.kind,
        recipient_email=payload.recipient_email,
        subject=payload.subject,
    )


@router.post("/clients/{client_id}/email", response_model=DocumentEmailRead)
async def send_client_document_email(
    client_id: str,
    payload: ClientDocumentEmailPayload,
    _: UserRead = Depends(require_permissions("clients.manage", "payments.manage")),
    service: DocumentService = Depends(get_document_service),
) -> DocumentEmailRead:
    return await service.send_client_document_email(
        client_id,
        kind=payload.kind,
        recipient_email=payload.recipient_email,
        subject=payload.subject,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )
