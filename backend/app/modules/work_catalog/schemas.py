from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
OptionalString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class WorkCatalogTemplateOperationCreate(BaseSchema):
    operation_id: str
    quantity: Decimal = Field(default=Decimal("1.00"), gt=0)
    note: OptionalString = None
    sort_order: int = Field(default=0, ge=0)


class WorkCatalogTemplateOperationRead(TimestampedReadSchema):
    operation_id: str
    operation_code: str
    operation_name: str
    quantity: Decimal
    note: Optional[str]
    sort_order: int


class WorkCatalogItemCreate(BaseSchema):
    code: ShortString
    name: ShortString
    category: Optional[ShortString] = None
    description: OptionalString = None
    base_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    default_duration_hours: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)
    default_operations: list[WorkCatalogTemplateOperationCreate] = Field(default_factory=list)


class WorkCatalogItemUpdate(BaseSchema):
    code: Optional[ShortString] = None
    name: Optional[ShortString] = None
    category: Optional[ShortString] = None
    description: OptionalString = None
    base_price: Optional[Decimal] = Field(default=None, ge=0)
    default_duration_hours: Optional[Decimal] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(default=None, ge=0)
    default_operations: Optional[list[WorkCatalogTemplateOperationCreate]] = None


class WorkCatalogItemRead(TimestampedReadSchema):
    code: str
    name: str
    category: Optional[str]
    description: Optional[str]
    base_price: Decimal
    default_duration_hours: Decimal
    is_active: bool
    sort_order: int
    default_operations: list[WorkCatalogTemplateOperationRead] = Field(default_factory=list)


class WorkCatalogItemListResponse(PaginatedResponse[WorkCatalogItemRead]):
    pass
