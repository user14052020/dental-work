from __future__ import annotations

from typing import Annotated, Optional

from pydantic import EmailStr, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
OptionalShortString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=255)]
PasswordString = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class EmployeeCreate(BaseSchema):
    full_name: NameString
    email: EmailStr
    password: PasswordString
    phone: Optional[PhoneString] = None
    job_title: OptionalShortString = None
    is_active: bool = True
    is_fired: bool = False
    executor_id: Optional[str] = None
    permission_codes: list[str] = []


class EmployeeUpdate(BaseSchema):
    full_name: Optional[NameString] = None
    email: Optional[EmailStr] = None
    password: Optional[PasswordString] = None
    phone: Optional[PhoneString] = None
    job_title: OptionalShortString = None
    is_active: Optional[bool] = None
    is_fired: Optional[bool] = None
    executor_id: Optional[str] = None
    permission_codes: Optional[list[str]] = None


class EmployeeRead(TimestampedReadSchema):
    full_name: str
    email: EmailStr
    phone: Optional[str]
    job_title: Optional[str]
    is_active: bool
    is_fired: bool
    permission_codes: list[str]
    executor_id: Optional[str]
    executor_name: Optional[str] = None
    is_technician: bool = False


class EmployeeListResponse(PaginatedResponse[EmployeeRead]):
    pass
