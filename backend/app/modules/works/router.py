from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_work_service
from app.modules.works.schemas import WorkCreate, WorkListResponse, WorkRead, WorkUpdateStatus
from app.modules.works.service import WorkService


router = APIRouter(prefix="/works", tags=["works"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=WorkListResponse)
async def list_works(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    client_id: Optional[str] = Query(default=None),
    executor_id: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: WorkService = Depends(get_work_service),
) -> WorkListResponse:
    return await service.list_works(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        client_id=client_id,
        executor_id=executor_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{work_id}", response_model=WorkRead)
async def get_work(work_id: str, service: WorkService = Depends(get_work_service)) -> WorkRead:
    return await service.get_work(work_id)


@router.post("", response_model=WorkRead, status_code=status.HTTP_201_CREATED)
async def create_work(payload: WorkCreate, service: WorkService = Depends(get_work_service)) -> WorkRead:
    return await service.create_work(payload)


@router.patch("/{work_id}/status", response_model=WorkRead)
async def update_status(
    work_id: str,
    payload: WorkUpdateStatus,
    service: WorkService = Depends(get_work_service),
) -> WorkRead:
    return await service.update_status(work_id, payload)
