from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.common.schemas import BaseSchema


class ReportsSummaryRead(BaseSchema):
    total_narads: int
    open_narads: int
    overdue_narads: int
    total_revenue: Decimal
    total_paid: Decimal
    total_balance_due: Decimal
    low_stock_materials: int
    payroll_total: Decimal
    actual_material_consumption_total: Decimal


class ClientBalanceReportItemRead(BaseSchema):
    client_id: str
    client_name: str
    narads_count: int
    works_count: int
    total_price: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    last_received_at: Optional[datetime] = None


class NaradReportItemRead(BaseSchema):
    narad_id: str
    narad_number: str
    title: str
    client_name: str
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    status: str
    works_count: int
    total_price: Decimal
    total_cost: Decimal
    total_margin: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    received_at: datetime
    deadline_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    is_overdue: bool = False


class ExecutorLoadReportItemRead(BaseSchema):
    executor_id: str
    executor_name: str
    active_works: int
    closed_works: int
    revenue_total: Decimal
    earnings_total: Decimal
    last_closed_at: Optional[datetime] = None


class MaterialStockReportItemRead(BaseSchema):
    material_id: str
    name: str
    category: Optional[str] = None
    unit: str
    stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    min_stock: Decimal
    stock_value: Decimal
    is_low_stock: bool = False


class PayrollReportItemRead(BaseSchema):
    executor_id: str
    executor_name: str
    narads_count: int
    operations_count: int
    quantity_total: Decimal
    earnings_total: Decimal
    last_closed_at: Optional[datetime] = None


class PayrollOperationReportItemRead(BaseSchema):
    executor_id: str
    executor_name: str
    operation_code: Optional[str] = None
    operation_name: str
    narads_count: int
    operations_count: int
    quantity_total: Decimal
    earnings_total: Decimal
    last_closed_at: Optional[datetime] = None


class ActualMaterialConsumptionReportItemRead(BaseSchema):
    movement_id: str
    movement_date: datetime
    material_id: str
    material_name: str
    material_category: Optional[str] = None
    unit: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    balance_after: Decimal
    reason: Optional[str] = None


class NaradMaterialConsumptionReportItemRead(BaseSchema):
    movement_id: str
    movement_date: datetime
    narad_id: str
    narad_number: str
    narad_title: str
    client_name: str
    work_id: str
    work_order_number: str
    material_id: str
    material_name: str
    material_category: Optional[str] = None
    unit: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    balance_after: Decimal
    reason: Optional[str] = None


class ReportsSnapshotRead(BaseSchema):
    summary: ReportsSummaryRead
    client_balances: list[ClientBalanceReportItemRead]
    narads: list[NaradReportItemRead]
    executors: list[ExecutorLoadReportItemRead]
    payroll: list[PayrollReportItemRead]
    payroll_operations: list[PayrollOperationReportItemRead]
    materials: list[MaterialStockReportItemRead]
    actual_material_consumption: list[ActualMaterialConsumptionReportItemRead]
    narad_material_consumption: list[NaradMaterialConsumptionReportItemRead]
    generated_at: datetime
