from __future__ import annotations

from typing import Annotated, Optional

from pydantic import EmailStr, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
LongString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]
AddressString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=500)]


class ContractorCreate(BaseSchema):
    name: ShortString
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: AddressString = None
    comment: LongString = None
    is_active: bool = True


class ContractorUpdate(BaseSchema):
    name: Optional[ShortString] = None
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: AddressString = None
    comment: LongString = None
    is_active: Optional[bool] = None


class ContractorRead(TimestampedReadSchema):
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    comment: Optional[str]
    is_active: bool


class ContractorListResponse(PaginatedResponse[ContractorRead]):
    pass
