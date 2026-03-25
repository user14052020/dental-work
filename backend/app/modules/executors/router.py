from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_executor_service, require_permissions
from app.modules.executors.schemas import ExecutorCreate, ExecutorListResponse, ExecutorRead, ExecutorUpdate
from app.modules.executors.service import ExecutorService


router = APIRouter(
    prefix="/executors",
    tags=["executors"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("executors.manage"))],
)


@router.get("", response_model=ExecutorListResponse)
async def list_executors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    service: ExecutorService = Depends(get_executor_service),
) -> ExecutorListResponse:
    return await service.list_executors(
        page=page, page_size=page_size, search=search, active_only=active_only
    )


@router.get("/{executor_id}", response_model=ExecutorRead)
async def get_executor(
    executor_id: str,
    service: ExecutorService = Depends(get_executor_service),
) -> ExecutorRead:
    return await service.get_executor(executor_id)


@router.post("", response_model=ExecutorRead, status_code=status.HTTP_201_CREATED)
async def create_executor(
    payload: ExecutorCreate,
    service: ExecutorService = Depends(get_executor_service),
) -> ExecutorRead:
    return await service.create_executor(payload)


@router.patch("/{executor_id}", response_model=ExecutorRead)
async def update_executor(
    executor_id: str,
    payload: ExecutorUpdate,
    service: ExecutorService = Depends(get_executor_service),
) -> ExecutorRead:
    return await service.update_executor(executor_id, payload)


@router.post("/{executor_id}/archive", response_model=ExecutorRead)
async def archive_executor(
    executor_id: str,
    service: ExecutorService = Depends(get_executor_service),
) -> ExecutorRead:
    return await service.archive_executor(executor_id)
