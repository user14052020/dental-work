from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.enums import PaymentMethod
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
LongString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=2000)]


class PaymentAllocationUpsert(BaseSchema):
    work_id: str
    amount: Decimal = Field(default=Decimal("0.00"), gt=0)


class PaymentNaradAllocationUpsert(BaseSchema):
    narad_id: str
    amount: Decimal = Field(default=Decimal("0.00"), gt=0)


class PaymentAllocationRead(TimestampedReadSchema):
    work_id: str
    narad_id: Optional[str] = None
    narad_number: Optional[str] = None
    narad_title: Optional[str] = None
    work_order_number: str
    work_type: str
    work_status: str
    received_at: datetime
    deadline_at: Optional[datetime] = None
    work_total: Decimal
    work_amount_paid: Decimal
    work_balance_due: Decimal
    amount: Decimal


class PaymentNaradAllocationRead(BaseSchema):
    narad_id: str
    narad_number: str
    narad_title: str
    narad_status: str
    received_at: datetime
    deadline_at: Optional[datetime] = None
    works_count: int
    total_price: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    amount: Decimal


class WorkPaymentCandidateRead(BaseSchema):
    work_id: str
    order_number: str
    work_type: str
    status: str
    received_at: datetime
    deadline_at: Optional[datetime] = None
    total_price: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    available_to_allocate: Decimal
    existing_allocation_amount: Decimal = Decimal("0.00")


class NaradPaymentCandidateRead(BaseSchema):
    narad_id: str
    narad_number: str
    title: str
    status: str
    received_at: datetime
    deadline_at: Optional[datetime] = None
    works_count: int
    total_price: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    available_to_allocate: Decimal
    existing_allocation_amount: Decimal = Decimal("0.00")


class PaymentCreate(BaseSchema):
    payment_number: Optional[ShortString] = None
    client_id: str
    payment_date: datetime
    method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    amount: Decimal = Field(default=Decimal("0.00"), gt=0)
    external_reference: Optional[ShortString] = None
    comment: LongString = None
    allocations: list[PaymentAllocationUpsert] = Field(default_factory=list)
    narad_allocations: Optional[list[PaymentNaradAllocationUpsert]] = None


class PaymentUpdate(BaseSchema):
    payment_number: Optional[ShortString] = None
    client_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    method: Optional[PaymentMethod] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    external_reference: Optional[ShortString] = None
    comment: LongString = None
    allocations: Optional[list[PaymentAllocationUpsert]] = None
    narad_allocations: Optional[list[PaymentNaradAllocationUpsert]] = None


class PaymentReturnNaradAllocation(BaseSchema):
    narad_id: str


class PaymentCompactRead(TimestampedReadSchema):
    payment_number: str
    client_id: str
    client_name: str
    payment_date: datetime
    method: str
    amount: Decimal
    allocated_total: Decimal
    unallocated_total: Decimal
    allocation_count: int
    external_reference: Optional[str] = None
    comment: Optional[str] = None


class PaymentRead(PaymentCompactRead):
    allocations: list[PaymentAllocationRead] = Field(default_factory=list)
    narad_allocations: list[PaymentNaradAllocationRead] = Field(default_factory=list)


class PaymentListResponse(PaginatedResponse[PaymentCompactRead]):
    pass
