from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_dashboard_service
from app.modules.dashboard.schemas import DashboardRead
from app.modules.dashboard.service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=DashboardRead)
async def get_dashboard(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardRead:
    return await service.get_overview(date_from=date_from, date_to=date_to)
