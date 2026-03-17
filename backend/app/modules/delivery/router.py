from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_current_user, get_delivery_service
from app.modules.auth.schemas import UserRead
from app.modules.delivery.schemas import DeliveryListResponse, DeliveryMarkSentPayload, DeliveryMarkSentResponse
from app.modules.delivery.service import DeliveryService


router = APIRouter(prefix="/delivery", tags=["delivery"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=DeliveryListResponse)
async def list_delivery_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=255),
    client_id: Optional[str] = Query(default=None),
    executor_id: Optional[str] = Query(default=None),
    sent: Optional[bool] = Query(default=False),
    service: DeliveryService = Depends(get_delivery_service),
) -> DeliveryListResponse:
    return await service.list_delivery_items(
        page=page,
        page_size=page_size,
        search=search,
        client_id=client_id,
        executor_id=executor_id,
        sent=sent,
    )


@router.post("/mark-sent", response_model=DeliveryMarkSentResponse)
async def mark_delivery_sent(
    payload: DeliveryMarkSentPayload,
    service: DeliveryService = Depends(get_delivery_service),
    current_user: UserRead = Depends(get_current_user),
) -> DeliveryMarkSentResponse:
    return await service.mark_sent(payload, actor_email=current_user.email)


@router.get("/manifest", response_class=HTMLResponse)
async def render_delivery_manifest(
    work_ids: list[str] = Query(...),
    service: DeliveryService = Depends(get_delivery_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_manifest(work_ids))
