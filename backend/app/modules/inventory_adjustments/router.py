from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_inventory_adjustment_service, require_permissions
from app.modules.inventory_adjustments.schemas import (
    InventoryAdjustmentCreate,
    InventoryAdjustmentListResponse,
    InventoryAdjustmentRead,
)
from app.modules.inventory_adjustments.service import InventoryAdjustmentService


router = APIRouter(
    prefix="/inventory-adjustments",
    tags=["inventory_adjustments"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("inventory.manage"))],
)


@router.get("", response_model=InventoryAdjustmentListResponse)
async def list_adjustments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: InventoryAdjustmentService = Depends(get_inventory_adjustment_service),
) -> InventoryAdjustmentListResponse:
    return await service.list_adjustments(
        page=page,
        page_size=page_size,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{adjustment_id}", response_model=InventoryAdjustmentRead)
async def get_adjustment(
    adjustment_id: str,
    service: InventoryAdjustmentService = Depends(get_inventory_adjustment_service),
) -> InventoryAdjustmentRead:
    return await service.get_adjustment(adjustment_id)


@router.post("", response_model=InventoryAdjustmentRead, status_code=status.HTTP_201_CREATED)
async def create_adjustment(
    payload: InventoryAdjustmentCreate,
    service: InventoryAdjustmentService = Depends(get_inventory_adjustment_service),
) -> InventoryAdjustmentRead:
    return await service.create_adjustment(payload)
