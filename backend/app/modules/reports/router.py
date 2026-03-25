from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_reports_service, require_permissions
from app.modules.reports.schemas import ReportsSnapshotRead
from app.modules.reports.service import ReportsService


router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user), Depends(require_permissions("reports.view"))],
)


@router.get("", response_model=ReportsSnapshotRead)
async def get_reports_snapshot(
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    service: ReportsService = Depends(get_reports_service),
) -> ReportsSnapshotRead:
    return await service.get_snapshot(date_from=date_from, date_to=date_to)
