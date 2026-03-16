from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import EmailStr, Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema
from app.modules.works.schemas import WorkCompactRead


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class ClientCreate(BaseSchema):
    name: ShortString
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)
    comment: CommentString = None


class ClientUpdate(BaseSchema):
    name: Optional[ShortString] = None
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)
    comment: CommentString = None


class ClientRead(TimestampedReadSchema):
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    comment: Optional[str]
    work_count: int = 0
    order_total: Decimal = Decimal("0.00")
    paid_total: Decimal = Decimal("0.00")
    unpaid_total: Decimal = Decimal("0.00")


class ClientDetailRead(ClientRead):
    recent_works: list[WorkCompactRead] = []


class ClientListResponse(PaginatedResponse[ClientRead]):
    pass
