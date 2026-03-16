from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, QuantityValue, TimestampedReadSchema


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class MaterialCreate(BaseSchema):
    name: NameString
    category: Optional[NameString] = None
    unit: NameString
    stock: QuantityValue
    purchase_price: Decimal
    average_price: Decimal
    supplier: Optional[NameString] = None
    min_stock: QuantityValue
    comment: CommentString = None


class MaterialUpdate(BaseSchema):
    name: Optional[NameString] = None
    category: Optional[NameString] = None
    unit: Optional[NameString] = None
    stock: Optional[QuantityValue] = None
    purchase_price: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    supplier: Optional[NameString] = None
    min_stock: Optional[QuantityValue] = None
    comment: CommentString = None


class MaterialConsume(BaseSchema):
    quantity: QuantityValue


class MaterialRead(TimestampedReadSchema):
    name: str
    category: Optional[str]
    unit: str
    stock: Decimal
    purchase_price: Decimal
    average_price: Decimal
    supplier: Optional[str]
    min_stock: Decimal
    comment: Optional[str]
    is_low_stock: bool = False


class MaterialListResponse(PaginatedResponse[MaterialRead]):
    pass
