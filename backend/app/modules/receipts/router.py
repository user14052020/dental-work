from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_material_receipt_service, require_permissions
from app.modules.receipts.schemas import (
    MaterialReceiptCreate,
    MaterialReceiptListResponse,
    MaterialReceiptRead,
)
from app.modules.receipts.service import MaterialReceiptService


router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("receipts.manage"))],
)


@router.get("", response_model=MaterialReceiptListResponse)
async def list_receipts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    supplier: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: MaterialReceiptService = Depends(get_material_receipt_service),
) -> MaterialReceiptListResponse:
    return await service.list_receipts(
        page=page,
        page_size=page_size,
        search=search,
        supplier=supplier,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{receipt_id}", response_model=MaterialReceiptRead)
async def get_receipt(
    receipt_id: str,
    service: MaterialReceiptService = Depends(get_material_receipt_service),
) -> MaterialReceiptRead:
    return await service.get_receipt(receipt_id)


@router.post("", response_model=MaterialReceiptRead, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    payload: MaterialReceiptCreate,
    service: MaterialReceiptService = Depends(get_material_receipt_service),
) -> MaterialReceiptRead:
    return await service.create_receipt(payload)
