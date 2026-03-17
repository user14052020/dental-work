from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user, get_work_service
from app.modules.auth.schemas import UserRead
from app.modules.operations.schemas import WorkOperationStatusUpdate
from app.modules.works.schemas import (
    WorkAttachmentRead,
    WorkClose,
    WorkCreate,
    WorkListResponse,
    WorkPayrollSummaryRead,
    WorkRead,
    WorkReopen,
    WorkUpdateStatus,
)
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
async def create_work(
    payload: WorkCreate,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkRead:
    return await service.create_work(payload, actor_email=current_user.email)


@router.patch("/{work_id}/status", response_model=WorkRead)
async def update_status(
    work_id: str,
    payload: WorkUpdateStatus,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkRead:
    return await service.update_status(work_id, payload, actor_email=current_user.email)


@router.post("/{work_id}/close", response_model=WorkRead)
async def close_work(
    work_id: str,
    payload: WorkClose,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkRead:
    return await service.close_work(work_id, payload, actor_email=current_user.email)


@router.post("/{work_id}/reopen", response_model=WorkRead)
async def reopen_work(
    work_id: str,
    payload: WorkReopen,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkRead:
    return await service.reopen_work(work_id, payload, actor_email=current_user.email)


@router.patch("/{work_id}/operations/{work_operation_id}/status", response_model=WorkRead)
async def update_operation_status(
    work_id: str,
    work_operation_id: str,
    payload: WorkOperationStatusUpdate,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkRead:
    return await service.update_operation_status(
        work_id,
        work_operation_id,
        payload,
        actor_email=current_user.email,
    )


@router.post("/{work_id}/attachments", response_model=WorkAttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_work_attachment(
    work_id: str,
    file: UploadFile = File(...),
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> WorkAttachmentRead:
    return await service.upload_attachment(work_id, file=file, actor_email=current_user.email)


@router.delete("/{work_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_attachment(
    work_id: str,
    attachment_id: str,
    service: WorkService = Depends(get_work_service),
    current_user: UserRead = Depends(get_current_user),
) -> Response:
    await service.delete_attachment(work_id, attachment_id, actor_email=current_user.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{work_id}/attachments/{attachment_id}/download", response_class=FileResponse)
async def download_work_attachment(
    work_id: str,
    attachment_id: str,
    service: WorkService = Depends(get_work_service),
) -> FileResponse:
    return await service.download_attachment(work_id, attachment_id)


@router.get("/payroll/summary", response_model=WorkPayrollSummaryRead)
async def get_payroll_summary(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    executor_id: Optional[str] = Query(default=None),
    service: WorkService = Depends(get_work_service),
) -> WorkPayrollSummaryRead:
    return await service.get_payroll_summary(date_from=date_from, date_to=date_to, executor_id=executor_id)
