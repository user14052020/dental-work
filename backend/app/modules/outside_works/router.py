from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_narad_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.narads.schemas import (
    NaradRead,
    OutsideWorkListResponse,
    OutsideWorkMarkReturned,
    OutsideWorkMarkSent,
)
from app.modules.narads.service import NaradService


router = APIRouter(
    prefix="/outside-works",
    tags=["outside_works"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("outside_works.manage"))],
)


@router.get("", response_model=OutsideWorkListResponse)
async def list_outside_works(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    client_id: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    service: NaradService = Depends(get_narad_service),
) -> OutsideWorkListResponse:
    return await service.list_outside_works(
        page=page,
        page_size=page_size,
        search=search,
        client_id=client_id,
        state=state,
    )


@router.post("/{narad_id}/mark-sent", response_model=NaradRead)
async def mark_outside_work_sent(
    narad_id: str,
    payload: OutsideWorkMarkSent,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("outside_works.manage")),
) -> NaradRead:
    return await service.mark_outside_sent(narad_id, payload, actor_email=current_user.email)


@router.post("/{narad_id}/mark-returned", response_model=NaradRead)
async def mark_outside_work_returned(
    narad_id: str,
    payload: OutsideWorkMarkReturned,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("outside_works.manage")),
) -> NaradRead:
    return await service.mark_outside_returned(narad_id, payload, actor_email=current_user.email)
