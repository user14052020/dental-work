from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_material_service, require_permissions
from app.modules.materials.schemas import (
    MaterialConsume,
    MaterialCreate,
    MaterialDetailRead,
    MaterialListResponse,
    MaterialRead,
    ManualMaterialConsumptionUpdate,
    MaterialUpdate,
)
from app.modules.materials.service import MaterialService


router = APIRouter(
    prefix="/materials",
    tags=["materials"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("materials.manage"))],
)


@router.get("", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    low_stock_only: bool = Query(default=False),
    service: MaterialService = Depends(get_material_service),
) -> MaterialListResponse:
    return await service.list_materials(
        page=page, page_size=page_size, search=search, low_stock_only=low_stock_only
    )


@router.get("/{material_id}", response_model=MaterialDetailRead)
async def get_material(
    material_id: str,
    service: MaterialService = Depends(get_material_service),
) -> MaterialDetailRead:
    return await service.get_material(material_id)


@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED)
async def create_material(
    payload: MaterialCreate,
    service: MaterialService = Depends(get_material_service),
) -> MaterialRead:
    return await service.create_material(payload)


@router.patch("/{material_id}", response_model=MaterialRead)
async def update_material(
    material_id: str,
    payload: MaterialUpdate,
    service: MaterialService = Depends(get_material_service),
) -> MaterialRead:
    return await service.update_material(material_id, payload)


@router.post("/{material_id}/consume", response_model=MaterialRead)
async def consume_material(
    material_id: str,
    payload: MaterialConsume,
    service: MaterialService = Depends(get_material_service),
) -> MaterialRead:
    return await service.consume_material(material_id, payload)


@router.patch("/manual-consumptions/{movement_id}", response_model=MaterialRead)
async def update_manual_consumption(
    movement_id: str,
    payload: ManualMaterialConsumptionUpdate,
    service: MaterialService = Depends(get_material_service),
) -> MaterialRead:
    return await service.update_manual_consumption(movement_id, payload)


@router.delete("/manual-consumptions/{movement_id}", response_model=MaterialRead)
async def delete_manual_consumption(
    movement_id: str,
    service: MaterialService = Depends(get_material_service),
) -> MaterialRead:
    return await service.delete_manual_consumption(movement_id)
