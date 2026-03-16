from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


Identifier = UUID
TrimmedString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
PhoneString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=7, max_length=20, pattern=r"^\+?[0-9()\-\s]{7,20}$"),
]
MoneyValue = Annotated[Decimal, Field(max_digits=12, decimal_places=2, ge=0)]
QuantityValue = Annotated[Decimal, Field(max_digits=12, decimal_places=3, ge=0)]


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampedReadSchema(BaseSchema):
    id: Identifier
    created_at: datetime
    updated_at: datetime
