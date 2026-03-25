from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_operation_service, require_permissions
from app.modules.operations.schemas import (
    ExecutorCategoryCreate,
    ExecutorCategoryListResponse,
    ExecutorCategoryRead,
    ExecutorCategoryUpdate,
    OperationCatalogCreate,
    OperationCatalogListResponse,
    OperationCatalogRead,
    OperationCatalogUpdate,
)
from app.modules.operations.service import OperationService


router = APIRouter(
    prefix="/operations",
    tags=["operations"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("operations.manage"))],
)


@router.get("/categories", response_model=ExecutorCategoryListResponse)
async def list_executor_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    service: OperationService = Depends(get_operation_service),
) -> ExecutorCategoryListResponse:
    return await service.list_categories(
        page=page,
        page_size=page_size,
        search=search,
        active_only=active_only,
    )


@router.get("/categories/{category_id}", response_model=ExecutorCategoryRead)
async def get_executor_category(
    category_id: str,
    service: OperationService = Depends(get_operation_service),
) -> ExecutorCategoryRead:
    return await service.get_category(category_id)


@router.post("/categories", response_model=ExecutorCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_executor_category(
    payload: ExecutorCategoryCreate,
    service: OperationService = Depends(get_operation_service),
) -> ExecutorCategoryRead:
    return await service.create_category(payload)


@router.patch("/categories/{category_id}", response_model=ExecutorCategoryRead)
async def update_executor_category(
    category_id: str,
    payload: ExecutorCategoryUpdate,
    service: OperationService = Depends(get_operation_service),
) -> ExecutorCategoryRead:
    return await service.update_category(category_id, payload)


@router.get("", response_model=OperationCatalogListResponse)
async def list_operations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    active_only: Optional[bool] = Query(default=None),
    service: OperationService = Depends(get_operation_service),
) -> OperationCatalogListResponse:
    return await service.list_operations(
        page=page,
        page_size=page_size,
        search=search,
        active_only=active_only,
    )


@router.get("/{operation_id}", response_model=OperationCatalogRead)
async def get_operation(
    operation_id: str,
    service: OperationService = Depends(get_operation_service),
) -> OperationCatalogRead:
    return await service.get_operation(operation_id)


@router.post("", response_model=OperationCatalogRead, status_code=status.HTTP_201_CREATED)
async def create_operation(
    payload: OperationCatalogCreate,
    service: OperationService = Depends(get_operation_service),
) -> OperationCatalogRead:
    return await service.create_operation(payload)


@router.patch("/{operation_id}", response_model=OperationCatalogRead)
async def update_operation(
    operation_id: str,
    payload: OperationCatalogUpdate,
    service: OperationService = Depends(get_operation_service),
) -> OperationCatalogRead:
    return await service.update_operation(operation_id, payload)
