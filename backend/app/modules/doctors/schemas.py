from __future__ import annotations

from typing import Annotated, Optional

from pydantic import EmailStr, Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class DoctorCreate(BaseSchema):
    client_id: Optional[str] = None
    full_name: ShortString
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    specialization: Optional[ShortString] = None
    comment: CommentString = None
    is_active: bool = True


class DoctorUpdate(BaseSchema):
    client_id: Optional[str] = None
    full_name: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    specialization: Optional[ShortString] = None
    comment: CommentString = None
    is_active: Optional[bool] = None


class DoctorRead(TimestampedReadSchema):
    client_id: Optional[str]
    client_name: Optional[str]
    full_name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    specialization: Optional[str]
    comment: Optional[str]
    is_active: bool


class DoctorListResponse(PaginatedResponse[DoctorRead]):
    pass
