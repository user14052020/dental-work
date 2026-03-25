from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from typing import Literal

from pydantic import Field

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, TimestampedReadSchema


class DeliveryItemRead(TimestampedReadSchema):
    narad_number: str
    title: str
    status: str
    client_id: str
    client_name: str
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_phone: Optional[str] = None
    works_count: int
    work_numbers: list[str] = Field(default_factory=list)
    work_types: list[str] = Field(default_factory=list)
    executor_names: list[str] = Field(default_factory=list)
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    received_at: datetime
    deadline_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivery_sent: bool = False
    delivery_sent_at: Optional[datetime] = None
    total_price: Decimal


class DeliveryListResponse(PaginatedResponse[DeliveryItemRead]):
    pass


class DeliveryMarkSentPayload(BaseSchema):
    narad_ids: list[str] = Field(min_length=1, max_length=100)


class DeliveryMarkSentResponse(BaseSchema):
    updated_count: int
    items: list[DeliveryItemRead]


DeliverySortBy = Literal["client_name", "deadline_at", "received_at"]
DeliverySortDirection = Literal["asc", "desc"]
