from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_narad_service, require_permissions
from app.modules.auth.schemas import UserRead
from app.modules.narads.schemas import (
    NaradClose,
    NaradCreate,
    NaradListResponse,
    NaradRead,
    NaradReopen,
    NaradUpdate,
)
from app.modules.narads.service import NaradService


router = APIRouter(
    prefix="/narads",
    tags=["narads"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("narads.manage"))],
)


@router.get("", response_model=NaradListResponse)
async def list_narads(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    client_id: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: NaradService = Depends(get_narad_service),
) -> NaradListResponse:
    return await service.list_narads(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        client_id=client_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{narad_id}", response_model=NaradRead)
async def get_narad(narad_id: str, service: NaradService = Depends(get_narad_service)) -> NaradRead:
    return await service.get_narad(narad_id)


@router.post("", response_model=NaradRead, status_code=status.HTTP_201_CREATED)
async def create_narad(
    payload: NaradCreate,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("narads.manage")),
) -> NaradRead:
    return await service.create_narad(payload, actor_email=current_user.email)


@router.patch("/{narad_id}", response_model=NaradRead)
async def update_narad(
    narad_id: str,
    payload: NaradUpdate,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("narads.manage")),
) -> NaradRead:
    return await service.update_narad(narad_id, payload, actor_email=current_user.email)


@router.post("/{narad_id}/reserve-materials", response_model=NaradRead)
async def reserve_narad_materials(
    narad_id: str,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("narads.manage")),
) -> NaradRead:
    return await service.reserve_materials(narad_id, actor_email=current_user.email)


@router.post("/{narad_id}/close", response_model=NaradRead)
async def close_narad(
    narad_id: str,
    payload: NaradClose,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("narads.manage")),
) -> NaradRead:
    return await service.close_narad(narad_id, payload, actor_email=current_user.email)


@router.post("/{narad_id}/reopen", response_model=NaradRead)
async def reopen_narad(
    narad_id: str,
    payload: NaradReopen,
    service: NaradService = Depends(get_narad_service),
    current_user: UserRead = Depends(require_permissions("narads.manage")),
) -> NaradRead:
    return await service.reopen_narad(narad_id, payload, actor_email=current_user.email)
