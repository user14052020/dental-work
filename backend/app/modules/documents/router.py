from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_current_user, get_document_service
from app.modules.documents.service import DocumentService


router = APIRouter(
    prefix="/documents/works",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/{work_id}/invoice", response_class=HTMLResponse)
async def render_invoice(
    work_id: str,
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_invoice(work_id))


@router.get("/{work_id}/act", response_class=HTMLResponse)
async def render_act(
    work_id: str,
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_act(work_id))


@router.get("/{work_id}/job-order", response_class=HTMLResponse)
async def render_job_order(
    work_id: str,
    service: DocumentService = Depends(get_document_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_job_order(work_id))
