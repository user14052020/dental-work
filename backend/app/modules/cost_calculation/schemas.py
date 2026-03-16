from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CostMaterialLine(BaseModel):
    material_id: str
    quantity: Decimal = Field(ge=0)
    unit_cost_override: Optional[Decimal] = Field(default=None, ge=0)


class CostCalculationRequest(BaseModel):
    materials: list[CostMaterialLine] = []
    labor_hours: Decimal = Field(default=Decimal("0.00"), ge=0)
    hourly_rate_override: Optional[Decimal] = Field(default=None, ge=0)
    executor_id: Optional[str] = None
    additional_expenses: Decimal = Field(default=Decimal("0.00"), ge=0)
    sale_price: Decimal = Field(default=Decimal("0.00"), ge=0)


class CostBreakdownLine(BaseModel):
    name: str
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal


class CostCalculationRead(BaseModel):
    materials_cost: Decimal
    labor_cost: Decimal
    additional_expenses: Decimal
    total_cost: Decimal
    sale_price: Decimal
    margin: Decimal
    profitability_percent: Decimal
    lines: list[CostBreakdownLine]
