from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_current_user, get_delivery_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.delivery.schemas import (
    DeliveryListResponse,
    DeliveryMarkSentPayload,
    DeliveryMarkSentResponse,
    DeliverySortBy,
    DeliverySortDirection,
)
from app.modules.delivery.service import DeliveryService


router = APIRouter(
    prefix="/delivery",
    tags=["delivery"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("delivery.manage"))],
)


@router.get("", response_model=DeliveryListResponse)
async def list_delivery_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=255),
    client_id: Optional[str] = Query(default=None),
    executor_id: Optional[str] = Query(default=None),
    sent: Optional[bool] = Query(default=False),
    sort_by: DeliverySortBy = Query(default="deadline_at"),
    sort_direction: DeliverySortDirection = Query(default="asc"),
    service: DeliveryService = Depends(get_delivery_service),
) -> DeliveryListResponse:
    return await service.list_delivery_items(
        page=page,
        page_size=page_size,
        search=search,
        client_id=client_id,
        executor_id=executor_id,
        sent=sent,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )


@router.post("/mark-sent", response_model=DeliveryMarkSentResponse)
async def mark_delivery_sent(
    payload: DeliveryMarkSentPayload,
    service: DeliveryService = Depends(get_delivery_service),
    current_user: UserRead = Depends(require_permissions("delivery.manage")),
) -> DeliveryMarkSentResponse:
    return await service.mark_sent(payload, actor_email=current_user.email)


@router.get("/manifest", response_class=HTMLResponse)
async def render_delivery_manifest(
    narad_ids: list[str] = Query(...),
    service: DeliveryService = Depends(get_delivery_service),
) -> HTMLResponse:
    return HTMLResponse(await service.render_manifest(narad_ids))
