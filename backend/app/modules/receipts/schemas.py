from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, QuantityValue, TimestampedReadSchema


ReceiptNumberString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class MaterialReceiptItemCreate(BaseSchema):
    material_id: str
    quantity: QuantityValue
    unit_price: Decimal = Field(ge=0)


class MaterialReceiptItemRead(TimestampedReadSchema):
    material_id: str
    material_name: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    sort_order: int


class MaterialReceiptCreate(BaseSchema):
    receipt_number: ReceiptNumberString
    received_at: datetime
    supplier: Optional[ReceiptNumberString] = None
    comment: CommentString = None
    items: list[MaterialReceiptItemCreate] = Field(default_factory=list, min_length=1)


class MaterialReceiptCompactRead(TimestampedReadSchema):
    receipt_number: str
    received_at: datetime
    supplier: Optional[str] = None
    items_count: int
    total_amount: Decimal
    total_quantity: Decimal


class MaterialReceiptRead(MaterialReceiptCompactRead):
    comment: Optional[str] = None
    items: list[MaterialReceiptItemRead]


class MaterialReceiptListResponse(PaginatedResponse[MaterialReceiptCompactRead]):
    pass
