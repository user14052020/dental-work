from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class DashboardTopItem(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    work_count: int
    amount: Decimal


class DashboardRead(BaseModel):
    active_works: int
    overdue_works: int
    revenue: Decimal
    profit: Decimal
    material_expenses: Decimal
    top_clients: list[DashboardTopItem]
    top_executors: list[DashboardTopItem]
    generated_at: datetime
