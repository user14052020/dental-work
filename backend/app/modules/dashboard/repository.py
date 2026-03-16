from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import WorkStatus
from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.work import Work, WorkMaterial


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overview(self, *, date_from: datetime | None, date_to: datetime | None) -> dict:
        period_filters = []
        if date_from:
            period_filters.append(Work.received_at >= date_from)
        if date_to:
            period_filters.append(Work.received_at <= date_to)

        active_statuses = [WorkStatus.NEW.value, WorkStatus.IN_PROGRESS.value, WorkStatus.IN_REVIEW.value]
        overdue_filter = (
            (Work.deadline_at < datetime.now(timezone.utc))
            & (~Work.status.in_([WorkStatus.COMPLETED.value, WorkStatus.DELIVERED.value, WorkStatus.CANCELLED.value]))
        )

        active_works = await self.session.scalar(select(func.count(Work.id)).where(Work.status.in_(active_statuses)))
        overdue_works = await self.session.scalar(select(func.count(Work.id)).where(overdue_filter))

        revenue_stmt = select(
            func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")),
            func.coalesce(func.sum(Work.margin), Decimal("0.00")),
        )
        material_expenses_stmt = select(func.coalesce(func.sum(WorkMaterial.total_cost), Decimal("0.00"))).join(
            Work, Work.id == WorkMaterial.work_id
        )

        for filter_expression in period_filters:
            revenue_stmt = revenue_stmt.where(filter_expression)
            material_expenses_stmt = material_expenses_stmt.where(filter_expression)

        revenue_row = await self.session.execute(revenue_stmt)
        revenue, profit = revenue_row.one()
        material_expenses = await self.session.scalar(material_expenses_stmt)

        top_clients_stmt = (
            select(
                Client.id,
                Client.name,
                func.count(Work.id).label("work_count"),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")).label("amount"),
            )
            .join(Work, Work.client_id == Client.id)
            .group_by(Client.id)
            .order_by(func.sum(Work.price_for_client).desc())
            .limit(5)
        )
        top_executors_stmt = (
            select(
                Executor.id,
                Executor.full_name,
                func.count(Work.id).label("work_count"),
                func.coalesce(func.sum(Work.margin), Decimal("0.00")).label("amount"),
            )
            .join(Work, Work.executor_id == Executor.id)
            .group_by(Executor.id)
            .order_by(func.sum(Work.margin).desc())
            .limit(5)
        )

        for filter_expression in period_filters:
            top_clients_stmt = top_clients_stmt.where(filter_expression)
            top_executors_stmt = top_executors_stmt.where(filter_expression)

        top_clients = [dict(row._mapping) for row in (await self.session.execute(top_clients_stmt)).all()]
        top_executors = [dict(row._mapping) for row in (await self.session.execute(top_executors_stmt)).all()]

        return {
            "active_works": int(active_works or 0),
            "overdue_works": int(overdue_works or 0),
            "revenue": revenue or Decimal("0.00"),
            "profit": profit or Decimal("0.00"),
            "material_expenses": material_expenses or Decimal("0.00"),
            "top_clients": top_clients,
            "top_executors": top_executors,
        }
