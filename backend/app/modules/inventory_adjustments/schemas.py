from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, QuantityValue, TimestampedReadSchema


AdjustmentNumberString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class InventoryAdjustmentItemCreate(BaseSchema):
    material_id: str
    actual_stock: QuantityValue
    comment: CommentString = None


class InventoryAdjustmentItemRead(TimestampedReadSchema):
    material_id: str
    material_name: str
    unit: str
    expected_stock: Decimal
    actual_stock: Decimal
    quantity_delta: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    sort_order: int
    comment: Optional[str] = None


class InventoryAdjustmentCreate(BaseSchema):
    adjustment_number: AdjustmentNumberString
    recorded_at: datetime
    comment: CommentString = None
    items: list[InventoryAdjustmentItemCreate] = Field(default_factory=list, min_length=1)


class InventoryAdjustmentCompactRead(TimestampedReadSchema):
    adjustment_number: str
    recorded_at: datetime
    items_count: int
    changed_items_count: int
    positive_delta_total: Decimal
    negative_delta_total: Decimal
    total_cost_impact: Decimal


class InventoryAdjustmentRead(InventoryAdjustmentCompactRead):
    comment: Optional[str] = None
    items: list[InventoryAdjustmentItemRead]


class InventoryAdjustmentListResponse(PaginatedResponse[InventoryAdjustmentCompactRead]):
    pass
