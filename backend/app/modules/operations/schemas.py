from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, StringConstraints

from app.common.enums import OperationExecutionStatus
from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, TimestampedReadSchema


NameString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
CodeString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
DescriptionString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=2000)]


class ExecutorCategoryCreate(BaseSchema):
    code: CodeString
    name: NameString
    description: DescriptionString = None
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


class ExecutorCategoryUpdate(BaseSchema):
    code: Optional[CodeString] = None
    name: Optional[NameString] = None
    description: DescriptionString = None
    sort_order: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ExecutorCategoryRead(TimestampedReadSchema):
    code: str
    name: str
    description: Optional[str]
    sort_order: int
    is_active: bool


class ExecutorCategoryListResponse(PaginatedResponse[ExecutorCategoryRead]):
    pass


class OperationCategoryRateCreate(BaseSchema):
    executor_category_id: str
    labor_rate: Decimal = Field(default=Decimal("0.00"), ge=0)


class OperationCategoryRateRead(TimestampedReadSchema):
    executor_category_id: str
    executor_category_code: str
    executor_category_name: str
    labor_rate: Decimal


class OperationCatalogCreate(BaseSchema):
    code: CodeString
    name: NameString
    operation_group: Optional[NameString] = None
    description: DescriptionString = None
    default_quantity: Decimal = Field(default=Decimal("1.00"), ge=0)
    default_duration_hours: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)
    rates: list[OperationCategoryRateCreate] = Field(default_factory=list)


class OperationCatalogUpdate(BaseSchema):
    code: Optional[CodeString] = None
    name: Optional[NameString] = None
    operation_group: Optional[NameString] = None
    description: DescriptionString = None
    default_quantity: Optional[Decimal] = Field(default=None, ge=0)
    default_duration_hours: Optional[Decimal] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(default=None, ge=0)
    rates: Optional[list[OperationCategoryRateCreate]] = None


class OperationCatalogRead(TimestampedReadSchema):
    code: str
    name: str
    operation_group: Optional[str]
    description: Optional[str]
    default_quantity: Decimal
    default_duration_hours: Decimal
    is_active: bool
    sort_order: int
    rates: list[OperationCategoryRateRead] = Field(default_factory=list)


class OperationCatalogListResponse(PaginatedResponse[OperationCatalogRead]):
    pass


class WorkOperationCreate(BaseSchema):
    operation_id: str
    executor_id: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1.00"), ge=0)
    unit_labor_cost_override: Optional[Decimal] = Field(default=None, ge=0)
    note: DescriptionString = None


class WorkOperationLogRead(TimestampedReadSchema):
    action: str
    actor_email: Optional[str]
    details: dict[str, object] = Field(default_factory=dict)


class WorkOperationRead(TimestampedReadSchema):
    operation_id: Optional[str]
    operation_code: Optional[str]
    operation_name: str
    executor_id: Optional[str]
    executor_name: Optional[str]
    executor_category_id: Optional[str]
    executor_category_name: Optional[str]
    quantity: Decimal
    unit_labor_cost: Decimal
    total_labor_cost: Decimal
    status: str
    sort_order: int
    manual_rate_override: bool
    note: Optional[str]
    logs: list[WorkOperationLogRead] = Field(default_factory=list)


class WorkOperationStatusUpdate(BaseSchema):
    status: OperationExecutionStatus
