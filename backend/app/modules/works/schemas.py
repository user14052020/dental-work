from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.enums import WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, QuantityValue, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
LongString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=2000)]


class WorkMaterialUsageCreate(BaseSchema):
    material_id: str
    quantity: QuantityValue


class WorkMaterialUsageRead(TimestampedReadSchema):
    material_id: str
    material_name: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal


class WorkCreate(BaseSchema):
    order_number: ShortString
    client_id: str
    executor_id: Optional[str] = None
    work_type: ShortString
    description: LongString = None
    status: WorkStatus = WorkStatus.NEW
    received_at: datetime
    deadline_at: Optional[datetime] = None
    price_for_client: Decimal = Field(default=Decimal("0.00"), ge=0)
    additional_expenses: Decimal = Field(default=Decimal("0.00"), ge=0)
    labor_hours: Decimal = Field(default=Decimal("0.00"), ge=0)
    amount_paid: Decimal = Field(default=Decimal("0.00"), ge=0)
    comment: LongString = None
    materials: list[WorkMaterialUsageCreate] = []


class WorkUpdateStatus(BaseSchema):
    status: WorkStatus
    completed_at: Optional[datetime] = None


class WorkCompactRead(TimestampedReadSchema):
    order_number: str
    work_type: str
    status: str
    received_at: datetime
    deadline_at: Optional[datetime]
    price_for_client: Decimal
    cost_price: Decimal
    margin: Decimal


class WorkRead(WorkCompactRead):
    client_id: str
    client_name: str
    executor_id: Optional[str]
    executor_name: Optional[str]
    description: Optional[str]
    completed_at: Optional[datetime]
    additional_expenses: Decimal
    labor_hours: Decimal
    amount_paid: Decimal
    comment: Optional[str]
    materials: list[WorkMaterialUsageRead] = []


class WorkListResponse(PaginatedResponse[WorkCompactRead]):
    pass
