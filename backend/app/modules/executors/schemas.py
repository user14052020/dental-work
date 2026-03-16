from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import EmailStr, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class ExecutorCreate(BaseSchema):
    full_name: NameString
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    specialization: Optional[NameString] = None
    hourly_rate: Decimal
    comment: CommentString = None
    is_active: bool = True


class ExecutorUpdate(BaseSchema):
    full_name: Optional[NameString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    specialization: Optional[NameString] = None
    hourly_rate: Optional[Decimal] = None
    comment: CommentString = None
    is_active: Optional[bool] = None


class ExecutorRead(TimestampedReadSchema):
    full_name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    specialization: Optional[str]
    hourly_rate: Decimal
    comment: Optional[str]
    is_active: bool
    work_count: int = 0
    production_total: Decimal = Decimal("0.00")


class ExecutorListResponse(PaginatedResponse[ExecutorRead]):
    pass
