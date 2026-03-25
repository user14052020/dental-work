from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints, field_validator

from app.common.enums import WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, QuantityValue, TimestampedReadSchema
from app.modules.operations.schemas import WorkOperationCreate, WorkOperationRead


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
    reserved_at: Optional[datetime] = None
    consumed_at: Optional[datetime] = None


class WorkAttachmentRead(TimestampedReadSchema):
    file_name: str
    content_type: str
    file_size: int
    uploaded_by_email: Optional[str]
    download_url: str


class WorkPaymentAllocationRead(TimestampedReadSchema):
    payment_id: str
    payment_number: str
    payment_date: datetime
    payment_method: str
    payment_amount: Decimal
    allocated_amount: Decimal
    payment_unallocated_total: Decimal
    external_reference: Optional[str] = None


class WorkItemCreate(BaseSchema):
    work_catalog_item_id: Optional[str] = None
    description: LongString = None
    quantity: Decimal = Field(default=Decimal("1.00"), gt=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)


class WorkItemRead(TimestampedReadSchema):
    work_catalog_item_id: Optional[str] = None
    work_catalog_item_code: Optional[str] = None
    work_catalog_item_name: Optional[str] = None
    work_catalog_item_category: Optional[str] = None
    work_type: str
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    sort_order: int


class WorkCreate(BaseSchema):
    narad_id: str
    executor_id: str
    work_catalog_item_id: str
    description: LongString = None
    status: WorkStatus = WorkStatus.NEW
    received_at: datetime
    deadline_at: Optional[datetime] = None
    base_price_for_client: Optional[Decimal] = Field(default=None, ge=0)
    price_adjustment_percent: Optional[Decimal] = Field(default=None, ge=-100, le=1000)
    price_for_client: Decimal = Field(default=Decimal("0.00"), ge=0)
    additional_expenses: Decimal = Field(default=Decimal("0.00"), ge=0)
    labor_hours: Decimal = Field(default=Decimal("0.00"), ge=0)
    amount_paid: Decimal = Field(default=Decimal("0.00"), ge=0)
    work_items: list[WorkItemCreate] = Field(default_factory=list)
    operations: list[WorkOperationCreate] = Field(default_factory=list)
    materials: list[WorkMaterialUsageCreate] = Field(default_factory=list)


class WorkUpdateStatus(BaseSchema):
    status: WorkStatus
    completed_at: Optional[datetime] = None


class WorkClose(BaseSchema):
    status: WorkStatus = WorkStatus.COMPLETED
    completed_at: Optional[datetime] = None
    note: LongString = None

    @field_validator("status")
    @classmethod
    def validate_close_status(cls, value: WorkStatus) -> WorkStatus:
        if value not in {WorkStatus.COMPLETED, WorkStatus.DELIVERED, WorkStatus.CANCELLED}:
            raise ValueError("Close status must be completed, delivered or cancelled.")
        return value


class WorkReopen(BaseSchema):
    status: WorkStatus = WorkStatus.IN_PROGRESS
    note: LongString = None

    @field_validator("status")
    @classmethod
    def validate_reopen_status(cls, value: WorkStatus) -> WorkStatus:
        if value not in {WorkStatus.NEW, WorkStatus.IN_PROGRESS, WorkStatus.IN_REVIEW}:
            raise ValueError("Reopen status must be new, in_progress or in_review.")
        return value


class WorkCompactRead(TimestampedReadSchema):
    narad_id: str
    narad_number: str
    order_number: str
    work_type: str
    work_catalog_item_id: Optional[str] = None
    status: str
    received_at: datetime
    deadline_at: Optional[datetime]
    delivery_sent: bool = False
    delivery_sent_at: Optional[datetime]
    is_closed: bool = False
    price_for_client: Decimal
    cost_price: Decimal
    margin: Decimal


class WorkRead(WorkCompactRead):
    executor_id: Optional[str]
    executor_name: Optional[str]
    work_catalog_item_code: Optional[str] = None
    work_catalog_item_name: Optional[str] = None
    work_catalog_item_category: Optional[str] = None
    description: Optional[str]
    completed_at: Optional[datetime]
    closed_at: Optional[datetime]
    base_price_for_client: Decimal
    price_adjustment_percent: Decimal
    additional_expenses: Decimal
    labor_hours: Decimal
    labor_cost: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    work_items: list[WorkItemRead] = Field(default_factory=list)
    attachments: list[WorkAttachmentRead] = Field(default_factory=list)
    payment_allocations: list[WorkPaymentAllocationRead] = Field(default_factory=list)
    operations: list[WorkOperationRead] = Field(default_factory=list)
    materials: list[WorkMaterialUsageRead] = Field(default_factory=list)
    change_logs: list["WorkChangeLogRead"] = Field(default_factory=list)


class WorkChangeLogRead(TimestampedReadSchema):
    action: str
    actor_email: Optional[str]
    details: dict[str, object] = {}


class ExecutorPayrollItemRead(BaseSchema):
    executor_id: str
    executor_name: str
    work_count: int
    earnings_total: Decimal
    revenue_total: Decimal
    closed_from: Optional[datetime] = None
    closed_to: Optional[datetime] = None


class WorkPayrollSummaryRead(BaseSchema):
    items: list[ExecutorPayrollItemRead]
    total_earnings: Decimal
    total_revenue: Decimal


class WorkListResponse(PaginatedResponse[WorkCompactRead]):
    pass
