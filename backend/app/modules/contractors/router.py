from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_contractor_service, get_current_user, require_permissions
from app.modules.contractors.schemas import (
    ContractorCreate,
    ContractorListResponse,
    ContractorRead,
    ContractorUpdate,
)
from app.modules.contractors.service import ContractorService


router = APIRouter(
    prefix="/contractors",
    tags=["contractors"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("contractors.manage"))],
)


@router.get("", response_model=ContractorListResponse)
async def list_contractors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    service: ContractorService = Depends(get_contractor_service),
) -> ContractorListResponse:
    return await service.list_contractors(
        page=page,
        page_size=page_size,
        search=search,
        active_only=active_only,
    )


@router.get("/{contractor_id}", response_model=ContractorRead)
async def get_contractor(
    contractor_id: str,
    service: ContractorService = Depends(get_contractor_service),
) -> ContractorRead:
    return await service.get_contractor(contractor_id)


@router.post("", response_model=ContractorRead, status_code=status.HTTP_201_CREATED)
async def create_contractor(
    payload: ContractorCreate,
    service: ContractorService = Depends(get_contractor_service),
) -> ContractorRead:
    return await service.create_contractor(payload)


@router.patch("/{contractor_id}", response_model=ContractorRead)
async def update_contractor(
    contractor_id: str,
    payload: ContractorUpdate,
    service: ContractorService = Depends(get_contractor_service),
) -> ContractorRead:
    return await service.update_contractor(contractor_id, payload)
