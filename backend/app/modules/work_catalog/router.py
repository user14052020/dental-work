from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_work_catalog_service, require_permissions
from app.modules.work_catalog.schemas import (
    WorkCatalogItemCreate,
    WorkCatalogItemListResponse,
    WorkCatalogItemRead,
    WorkCatalogItemUpdate,
)
from app.modules.work_catalog.service import WorkCatalogService


router = APIRouter(
    prefix="/work-catalog",
    tags=["work_catalog"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("work_catalog.manage"))],
)


@router.get("", response_model=WorkCatalogItemListResponse)
async def list_work_catalog_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    category: Optional[str] = Query(default=None),
    service: WorkCatalogService = Depends(get_work_catalog_service),
) -> WorkCatalogItemListResponse:
    return await service.list_items(
        page=page,
        page_size=page_size,
        search=search,
        active_only=active_only,
        category=category,
    )


@router.get("/{item_id}", response_model=WorkCatalogItemRead)
async def get_work_catalog_item(
    item_id: str,
    service: WorkCatalogService = Depends(get_work_catalog_service),
) -> WorkCatalogItemRead:
    return await service.get_item(item_id)


@router.post("", response_model=WorkCatalogItemRead, status_code=status.HTTP_201_CREATED)
async def create_work_catalog_item(
    payload: WorkCatalogItemCreate,
    service: WorkCatalogService = Depends(get_work_catalog_service),
) -> WorkCatalogItemRead:
    return await service.create_item(payload)


@router.patch("/{item_id}", response_model=WorkCatalogItemRead)
async def update_work_catalog_item(
    item_id: str,
    payload: WorkCatalogItemUpdate,
    service: WorkCatalogService = Depends(get_work_catalog_service),
) -> WorkCatalogItemRead:
    return await service.update_item(item_id, payload)
