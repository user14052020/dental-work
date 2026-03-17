from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints, field_validator

from app.common.enums import FaceShape, PatientGender, ToothSelectionState, ToothSurface, WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, QuantityValue, TimestampedReadSchema
from app.modules.operations.schemas import WorkOperationCreate, WorkOperationRead


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
LongString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=2000)]
ToothCodeString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^(?:[1-4][1-8]|[5-8][1-5])$", min_length=2, max_length=2),
]


class ToothSelectionItem(BaseSchema):
    tooth_code: ToothCodeString
    state: ToothSelectionState = ToothSelectionState.TARGET
    surfaces: list[ToothSurface] = Field(default_factory=list)

    @field_validator("surfaces")
    @classmethod
    def deduplicate_surfaces(cls, value: list[ToothSurface]) -> list[ToothSurface]:
        return list(dict.fromkeys(value))


class WorkMaterialUsageCreate(BaseSchema):
    material_id: str
    quantity: QuantityValue


class WorkMaterialUsageRead(TimestampedReadSchema):
    material_id: str
    material_name: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal


class WorkAttachmentRead(TimestampedReadSchema):
    file_name: str
    content_type: str
    file_size: int
    uploaded_by_email: Optional[str]
    download_url: str


class WorkItemCreate(BaseSchema):
    work_catalog_item_id: Optional[str] = None
    work_type: Optional[ShortString] = None
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
    order_number: ShortString
    client_id: str
    executor_id: Optional[str] = None
    doctor_id: Optional[str] = None
    work_catalog_item_id: Optional[str] = None
    work_type: Optional[ShortString] = None
    description: LongString = None
    doctor_name: Optional[ShortString] = None
    doctor_phone: Optional[PhoneString] = None
    patient_name: Optional[ShortString] = None
    patient_age: Optional[int] = Field(default=None, ge=0, le=130)
    patient_gender: Optional[PatientGender] = None
    require_color_photo: bool = False
    face_shape: Optional[FaceShape] = None
    implant_system: Optional[ShortString] = None
    metal_type: Optional[ShortString] = None
    shade_color: Optional[ShortString] = None
    tooth_formula: Optional[str] = Field(default=None, max_length=255)
    tooth_selection: list[ToothSelectionItem] = Field(default_factory=list)
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
    order_number: str
    work_type: str
    doctor_id: Optional[str] = None
    work_catalog_item_id: Optional[str] = None
    doctor_name: Optional[str]
    doctor_phone: Optional[str]
    patient_name: Optional[str]
    patient_age: Optional[int]
    patient_gender: Optional[str]
    require_color_photo: bool = False
    face_shape: Optional[str]
    implant_system: Optional[str]
    metal_type: Optional[str]
    shade_color: Optional[str]
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
    client_id: str
    client_name: str
    executor_id: Optional[str]
    executor_name: Optional[str]
    work_catalog_item_code: Optional[str] = None
    work_catalog_item_name: Optional[str] = None
    work_catalog_item_category: Optional[str] = None
    description: Optional[str]
    tooth_formula: Optional[str]
    tooth_selection: list[ToothSelectionItem] = Field(default_factory=list)
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
