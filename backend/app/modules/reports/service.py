from __future__ import annotations

from datetime import datetime, timezone

from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.reports.schemas import (
    ActualMaterialConsumptionReportItemRead,
    ClientBalanceReportItemRead,
    ExecutorLoadReportItemRead,
    MaterialStockReportItemRead,
    NaradReportItemRead,
    NaradMaterialConsumptionReportItemRead,
    PayrollOperationReportItemRead,
    PayrollReportItemRead,
    ReportsSnapshotRead,
    ReportsSummaryRead,
)


class ReportsService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def get_snapshot(
        self,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> ReportsSnapshotRead:
        async with self._uow as uow:
            snapshot = await uow.reports.get_snapshot(date_from=date_from, date_to=date_to)

        return ReportsSnapshotRead(
            summary=ReportsSummaryRead.model_validate(snapshot["summary"]),
            client_balances=[
                ClientBalanceReportItemRead.model_validate(item) for item in snapshot["client_balances"]
            ],
            narads=[
                NaradReportItemRead.model_validate(
                    {
                        **item,
                        "is_overdue": bool(
                            item.get("deadline_at")
                            and item.get("deadline_at") < datetime.now(timezone.utc)
                            and item.get("status") not in {"completed", "delivered", "cancelled"}
                        ),
                    }
                )
                for item in snapshot["narads"]
            ],
            executors=[
                ExecutorLoadReportItemRead.model_validate(item) for item in snapshot["executors"]
            ],
            payroll=[
                PayrollReportItemRead.model_validate(item) for item in snapshot["payroll"]
            ],
            payroll_operations=[
                PayrollOperationReportItemRead.model_validate(item) for item in snapshot["payroll_operations"]
            ],
            materials=[
                MaterialStockReportItemRead.model_validate(item) for item in snapshot["materials"]
            ],
            actual_material_consumption=[
                ActualMaterialConsumptionReportItemRead.model_validate(item)
                for item in snapshot["actual_material_consumption"]
            ],
            narad_material_consumption=[
                NaradMaterialConsumptionReportItemRead.model_validate(item)
                for item in snapshot["narad_material_consumption"]
            ],
            generated_at=datetime.now(timezone.utc),
        )
