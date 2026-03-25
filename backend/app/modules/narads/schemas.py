from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints, field_validator

from app.common.enums import FaceShape, PatientGender, ToothSelectionState, ToothSurface, WorkStatus
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


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


class NaradCreate(BaseSchema):
    narad_number: ShortString
    client_id: str
    doctor_id: Optional[str] = None
    contractor_id: Optional[str] = None
    title: ShortString
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
    received_at: datetime
    deadline_at: Optional[datetime] = None
    is_outside_work: bool = False
    outside_lab_name: Optional[ShortString] = None
    outside_order_number: Optional[ShortString] = None
    outside_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    outside_sent_at: Optional[datetime] = None
    outside_due_at: Optional[datetime] = None
    outside_returned_at: Optional[datetime] = None
    outside_comment: LongString = None


class NaradUpdate(BaseSchema):
    narad_number: Optional[ShortString] = None
    client_id: Optional[str] = None
    doctor_id: Optional[str] = None
    contractor_id: Optional[str] = None
    title: Optional[ShortString] = None
    description: LongString = None
    doctor_name: Optional[ShortString] = None
    doctor_phone: Optional[PhoneString] = None
    patient_name: Optional[ShortString] = None
    patient_age: Optional[int] = Field(default=None, ge=0, le=130)
    patient_gender: Optional[PatientGender] = None
    require_color_photo: Optional[bool] = None
    face_shape: Optional[FaceShape] = None
    implant_system: Optional[ShortString] = None
    metal_type: Optional[ShortString] = None
    shade_color: Optional[ShortString] = None
    tooth_formula: Optional[str] = Field(default=None, max_length=255)
    tooth_selection: Optional[list[ToothSelectionItem]] = None
    received_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    is_outside_work: Optional[bool] = None
    outside_lab_name: Optional[ShortString] = None
    outside_order_number: Optional[ShortString] = None
    outside_cost: Optional[Decimal] = Field(default=None, ge=0)
    outside_sent_at: Optional[datetime] = None
    outside_due_at: Optional[datetime] = None
    outside_returned_at: Optional[datetime] = None
    outside_comment: LongString = None


class OutsideWorkMarkSent(BaseSchema):
    contractor_id: Optional[str] = None
    outside_lab_name: Optional[ShortString] = None
    outside_order_number: Optional[ShortString] = None
    outside_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    outside_sent_at: datetime
    outside_due_at: Optional[datetime] = None
    outside_comment: LongString = None

    @field_validator("outside_lab_name")
    @classmethod
    def validate_outside_lab_name(cls, value: Optional[str], info):
        contractor_id = info.data.get("contractor_id")
        if contractor_id or (value and value.strip()):
            return value
        raise ValueError("Provide contractor_id or outside_lab_name.")


class OutsideWorkMarkReturned(BaseSchema):
    outside_returned_at: datetime
    outside_comment: LongString = None


class NaradClose(BaseSchema):
    status: WorkStatus = WorkStatus.COMPLETED
    completed_at: Optional[datetime] = None
    note: LongString = None

    @field_validator("status")
    @classmethod
    def validate_close_status(cls, value: WorkStatus) -> WorkStatus:
        if value not in {WorkStatus.COMPLETED, WorkStatus.DELIVERED, WorkStatus.CANCELLED}:
            raise ValueError("Close status must be completed, delivered or cancelled.")
        return value


class NaradReopen(BaseSchema):
    status: WorkStatus = WorkStatus.IN_PROGRESS
    note: LongString = None

    @field_validator("status")
    @classmethod
    def validate_reopen_status(cls, value: WorkStatus) -> WorkStatus:
        if value not in {WorkStatus.NEW, WorkStatus.IN_PROGRESS, WorkStatus.IN_REVIEW}:
            raise ValueError("Reopen status must be new, in_progress or in_review.")
        return value


class NaradWorkRead(TimestampedReadSchema):
    order_number: str
    work_type: str
    status: str
    executor_id: Optional[str] = None
    executor_name: Optional[str] = None
    work_catalog_item_code: Optional[str] = None
    work_catalog_item_name: Optional[str] = None
    price_for_client: Decimal
    cost_price: Decimal
    margin: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    received_at: datetime
    deadline_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class NaradStatusLogRead(TimestampedReadSchema):
    action: str
    actor_email: Optional[str] = None
    from_status: Optional[str] = None
    to_status: str
    note: Optional[str] = None
    details: dict[str, object] = {}


class NaradPaymentRead(TimestampedReadSchema):
    payment_number: str
    payment_date: datetime
    method: str
    amount: Decimal
    amount_allocated_to_narad: Decimal
    external_reference: Optional[str] = None
    comment: Optional[str] = None


class NaradCompactRead(TimestampedReadSchema):
    narad_number: str
    title: str
    client_id: str
    client_name: str
    client_email: Optional[str] = None
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    contractor_id: Optional[str] = None
    contractor_name: Optional[str] = None
    patient_name: Optional[str] = None
    require_color_photo: bool = False
    face_shape: Optional[str] = None
    implant_system: Optional[str] = None
    metal_type: Optional[str] = None
    shade_color: Optional[str] = None
    tooth_formula: Optional[str] = None
    status: str
    received_at: datetime
    deadline_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    is_outside_work: bool = False
    outside_lab_name: Optional[str] = None
    outside_order_number: Optional[str] = None
    outside_cost: Decimal = Decimal("0.00")
    outside_sent_at: Optional[datetime] = None
    outside_due_at: Optional[datetime] = None
    outside_returned_at: Optional[datetime] = None
    outside_comment: Optional[str] = None
    is_closed: bool = False
    works_count: int
    total_price: Decimal
    total_cost: Decimal
    total_margin: Decimal
    amount_paid: Decimal
    balance_due: Decimal


class NaradRead(NaradCompactRead):
    title: str
    description: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    tooth_selection: list[ToothSelectionItem] = Field(default_factory=list)
    works: list[NaradWorkRead]
    payments: list[NaradPaymentRead] = Field(default_factory=list)
    status_logs: list[NaradStatusLogRead]


class OutsideWorkItemRead(BaseSchema):
    narad_id: str
    narad_number: str
    title: str
    client_name: str
    contractor_id: Optional[str] = None
    contractor_name: Optional[str] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    status: str
    works_count: int
    work_numbers: list[str] = Field(default_factory=list)
    work_types: list[str] = Field(default_factory=list)
    outside_lab_name: Optional[str] = None
    outside_order_number: Optional[str] = None
    outside_cost: Decimal = Decimal("0.00")
    outside_sent_at: Optional[datetime] = None
    outside_due_at: Optional[datetime] = None
    outside_returned_at: Optional[datetime] = None
    outside_comment: Optional[str] = None
    outside_status: str
    is_outside_overdue: bool = False
    received_at: datetime
    deadline_at: Optional[datetime] = None


class OutsideWorkListResponse(PaginatedResponse[OutsideWorkItemRead]):
    pass


class NaradListResponse(PaginatedResponse[NaradCompactRead]):
    pass
