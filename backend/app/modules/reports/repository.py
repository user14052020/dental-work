from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import StockMovementType, WorkStatus
from app.db.models.client import Client
from app.db.models.executor import Executor
from app.db.models.material import Material
from app.db.models.material_receipt import StockMovement
from app.db.models.narad import Narad
from app.db.models.operation import WorkOperation
from app.db.models.work import Work


TWO_PLACES = Decimal("0.01")


class ReportsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_snapshot(self, *, date_from: datetime | None, date_to: datetime | None) -> dict[str, object]:
        work_period_filters = []
        narad_period_filters = []
        closed_work_period_filters = [Work.closed_at.is_not(None)]
        actual_consumption_filters = [
            StockMovement.movement_type == StockMovementType.CONSUME.value,
            StockMovement.work_id.is_(None),
        ]
        if date_from:
            work_period_filters.append(Work.received_at >= date_from)
            narad_period_filters.append(Narad.received_at >= date_from)
            closed_work_period_filters.append(Work.closed_at >= date_from)
            actual_consumption_filters.append(StockMovement.created_at >= date_from)
        if date_to:
            work_period_filters.append(Work.received_at <= date_to)
            narad_period_filters.append(Narad.received_at <= date_to)
            closed_work_period_filters.append(Work.closed_at <= date_to)
            actual_consumption_filters.append(StockMovement.created_at <= date_to)

        balance_expr = func.greatest(Work.price_for_client - Work.amount_paid, Decimal("0.00"))
        now = datetime.now(timezone.utc)
        terminal_statuses = [
            WorkStatus.COMPLETED.value,
            WorkStatus.DELIVERED.value,
            WorkStatus.CANCELLED.value,
        ]
        active_statuses = [
            WorkStatus.NEW.value,
            WorkStatus.IN_PROGRESS.value,
            WorkStatus.IN_REVIEW.value,
        ]

        summary_stmt = select(
            func.count(sa.distinct(Narad.id)).label("total_narads"),
            func.coalesce(
                func.sum(sa.case((Narad.status.in_(active_statuses), 1), else_=0)),
                0,
            ).label("open_narads"),
            func.coalesce(
                func.sum(
                    sa.case(
                        (
                            and_(
                                Narad.deadline_at.is_not(None),
                                Narad.deadline_at < now,
                                ~Narad.status.in_(terminal_statuses),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("overdue_narads"),
        ).select_from(Narad)
        if narad_period_filters:
            summary_stmt = summary_stmt.where(and_(*narad_period_filters))

        revenue_stmt = select(
            func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")).label("total_revenue"),
            func.coalesce(func.sum(Work.amount_paid), Decimal("0.00")).label("total_paid"),
            func.coalesce(func.sum(balance_expr), Decimal("0.00")).label("total_balance_due"),
        ).select_from(Work)
        if work_period_filters:
            revenue_stmt = revenue_stmt.where(and_(*work_period_filters))

        low_stock_stmt = select(func.count(Material.id)).where(Material.stock <= Material.min_stock)

        payroll_total_stmt = (
            select(func.coalesce(func.sum(WorkOperation.total_labor_cost), Decimal("0.00")))
            .select_from(WorkOperation)
            .join(Work, Work.id == WorkOperation.work_id)
            .where(and_(*closed_work_period_filters))
        )

        actual_material_consumption_total_stmt = (
            select(func.coalesce(func.sum(StockMovement.total_cost), Decimal("0.00")))
            .select_from(StockMovement)
            .where(and_(*actual_consumption_filters))
        )

        client_balances_stmt: Select = (
            select(
                Client.id.label("client_id"),
                Client.name.label("client_name"),
                func.count(Work.id).label("works_count"),
                func.count(sa.distinct(Work.narad_id)).label("narads_count"),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")).label("total_price"),
                func.coalesce(func.sum(Work.amount_paid), Decimal("0.00")).label("amount_paid"),
                func.coalesce(func.sum(balance_expr), Decimal("0.00")).label("balance_due"),
                func.max(Work.received_at).label("last_received_at"),
            )
            .join(Work, Work.client_id == Client.id)
            .group_by(Client.id, Client.name)
            .order_by(sa.desc("balance_due"), sa.desc("total_price"), Client.name.asc())
            .limit(15)
        )
        if work_period_filters:
            client_balances_stmt = client_balances_stmt.where(and_(*work_period_filters))

        narads_stmt: Select = (
            select(
                Narad.id.label("narad_id"),
                Narad.narad_number.label("narad_number"),
                Narad.title.label("title"),
                Client.name.label("client_name"),
                Narad.doctor_name.label("doctor_name"),
                Narad.patient_name.label("patient_name"),
                Narad.status.label("status"),
                func.count(Work.id).label("works_count"),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")).label("total_price"),
                (
                    func.coalesce(func.sum(Work.cost_price), Decimal("0.00"))
                    + func.coalesce(Narad.outside_cost, Decimal("0.00"))
                ).label("total_cost"),
                (
                    func.coalesce(func.sum(Work.margin), Decimal("0.00"))
                    - func.coalesce(Narad.outside_cost, Decimal("0.00"))
                ).label("total_margin"),
                func.coalesce(func.sum(Work.amount_paid), Decimal("0.00")).label("amount_paid"),
                func.coalesce(func.sum(balance_expr), Decimal("0.00")).label("balance_due"),
                Narad.received_at.label("received_at"),
                Narad.deadline_at.label("deadline_at"),
                Narad.completed_at.label("completed_at"),
                Narad.closed_at.label("closed_at"),
            )
            .join(Client, Client.id == Narad.client_id)
            .outerjoin(Work, Work.narad_id == Narad.id)
            .group_by(
                Narad.id,
                Narad.narad_number,
                Narad.title,
                Client.name,
                Narad.doctor_name,
                Narad.patient_name,
                Narad.status,
                Narad.outside_cost,
                Narad.received_at,
                Narad.deadline_at,
                Narad.completed_at,
                Narad.closed_at,
            )
            .order_by(Narad.received_at.desc(), Narad.created_at.desc())
            .limit(50)
        )
        if narad_period_filters:
            narads_stmt = narads_stmt.where(and_(*narad_period_filters))

        executors_stmt: Select = (
            select(
                Executor.id.label("executor_id"),
                Executor.full_name.label("executor_name"),
                func.coalesce(
                    func.sum(sa.case((Work.status.in_(active_statuses), 1), else_=0)),
                    0,
                ).label("active_works"),
                func.coalesce(
                    func.sum(sa.case((Work.closed_at.is_not(None), 1), else_=0)),
                    0,
                ).label("closed_works"),
                func.coalesce(func.sum(Work.price_for_client), Decimal("0.00")).label("revenue_total"),
                func.coalesce(func.sum(Work.labor_cost), Decimal("0.00")).label("earnings_total"),
                func.max(Work.closed_at).label("last_closed_at"),
            )
            .outerjoin(Work, Work.executor_id == Executor.id)
            .group_by(Executor.id, Executor.full_name)
            .order_by(sa.desc("active_works"), sa.desc("earnings_total"), Executor.full_name.asc())
            .limit(20)
        )
        if work_period_filters:
            executors_stmt = executors_stmt.where(and_(*work_period_filters))

        payroll_stmt: Select = (
            select(
                Executor.id.label("executor_id"),
                Executor.full_name.label("executor_name"),
                func.count(sa.distinct(Work.narad_id)).label("narads_count"),
                func.count(WorkOperation.id).label("operations_count"),
                func.coalesce(func.sum(WorkOperation.quantity), Decimal("0.00")).label("quantity_total"),
                func.coalesce(func.sum(WorkOperation.total_labor_cost), Decimal("0.00")).label("earnings_total"),
                func.max(Work.closed_at).label("last_closed_at"),
            )
            .select_from(WorkOperation)
            .join(Executor, Executor.id == WorkOperation.executor_id)
            .join(Work, Work.id == WorkOperation.work_id)
            .where(and_(*closed_work_period_filters))
            .group_by(Executor.id, Executor.full_name)
            .order_by(sa.desc("earnings_total"), Executor.full_name.asc())
            .limit(50)
        )

        payroll_operations_stmt: Select = (
            select(
                Executor.id.label("executor_id"),
                Executor.full_name.label("executor_name"),
                WorkOperation.operation_code.label("operation_code"),
                WorkOperation.operation_name.label("operation_name"),
                func.count(sa.distinct(Work.narad_id)).label("narads_count"),
                func.count(WorkOperation.id).label("operations_count"),
                func.coalesce(func.sum(WorkOperation.quantity), Decimal("0.00")).label("quantity_total"),
                func.coalesce(func.sum(WorkOperation.total_labor_cost), Decimal("0.00")).label("earnings_total"),
                func.max(Work.closed_at).label("last_closed_at"),
            )
            .select_from(WorkOperation)
            .join(Executor, Executor.id == WorkOperation.executor_id)
            .join(Work, Work.id == WorkOperation.work_id)
            .where(and_(*closed_work_period_filters))
            .group_by(
                Executor.id,
                Executor.full_name,
                WorkOperation.operation_code,
                WorkOperation.operation_name,
            )
            .order_by(sa.desc("earnings_total"), Executor.full_name.asc(), WorkOperation.operation_name.asc())
            .limit(100)
        )

        materials_stmt = (
            select(
                Material.id.label("material_id"),
                Material.name.label("name"),
                Material.category.label("category"),
                Material.unit.label("unit"),
                Material.stock.label("stock"),
                Material.reserved_stock.label("reserved_stock"),
                (Material.stock - Material.reserved_stock).label("available_stock"),
                Material.min_stock.label("min_stock"),
                (Material.stock * Material.average_price).label("stock_value"),
                sa.case((Material.stock <= Material.min_stock, True), else_=False).label("is_low_stock"),
            )
            .order_by(
                sa.desc(sa.case((Material.stock <= Material.min_stock, 1), else_=0)),
                (Material.stock - Material.reserved_stock).asc(),
                Material.name.asc(),
            )
            .limit(50)
        )

        actual_material_consumption_stmt = (
            select(
                StockMovement.id.label("movement_id"),
                StockMovement.created_at.label("movement_date"),
                Material.id.label("material_id"),
                Material.name.label("material_name"),
                Material.category.label("material_category"),
                Material.unit.label("unit"),
                func.abs(StockMovement.quantity_delta).label("quantity"),
                StockMovement.unit_cost.label("unit_cost"),
                StockMovement.total_cost.label("total_cost"),
                StockMovement.balance_after.label("balance_after"),
                StockMovement.comment.label("reason"),
            )
            .select_from(StockMovement)
            .join(Material, Material.id == StockMovement.material_id)
            .where(and_(*actual_consumption_filters))
            .order_by(StockMovement.created_at.desc(), Material.name.asc())
            .limit(100)
        )

        narad_material_consumption_filters = [
            StockMovement.movement_type == StockMovementType.CONSUME.value,
            StockMovement.work_id.is_not(None),
        ]
        if date_from:
            narad_material_consumption_filters.append(StockMovement.created_at >= date_from)
        if date_to:
            narad_material_consumption_filters.append(StockMovement.created_at <= date_to)

        narad_material_consumption_stmt = (
            select(
                StockMovement.id.label("movement_id"),
                StockMovement.created_at.label("movement_date"),
                Narad.id.label("narad_id"),
                Narad.narad_number.label("narad_number"),
                Narad.title.label("narad_title"),
                Client.name.label("client_name"),
                Work.id.label("work_id"),
                Work.order_number.label("work_order_number"),
                Material.id.label("material_id"),
                Material.name.label("material_name"),
                Material.category.label("material_category"),
                Material.unit.label("unit"),
                func.abs(StockMovement.quantity_delta).label("quantity"),
                StockMovement.unit_cost.label("unit_cost"),
                StockMovement.total_cost.label("total_cost"),
                StockMovement.balance_after.label("balance_after"),
                StockMovement.comment.label("reason"),
            )
            .select_from(StockMovement)
            .join(Material, Material.id == StockMovement.material_id)
            .join(Work, Work.id == StockMovement.work_id)
            .join(Narad, Narad.id == Work.narad_id)
            .join(Client, Client.id == Narad.client_id)
            .where(and_(*narad_material_consumption_filters))
            .order_by(StockMovement.created_at.desc(), Narad.narad_number.asc(), Work.order_number.asc())
            .limit(200)
        )

        summary_row = (await self.session.execute(summary_stmt)).one()
        revenue_row = (await self.session.execute(revenue_stmt)).one()
        low_stock_materials = await self.session.scalar(low_stock_stmt)
        payroll_total = await self.session.scalar(payroll_total_stmt)
        actual_material_consumption_total = await self.session.scalar(actual_material_consumption_total_stmt)
        client_balances = [dict(row._mapping) for row in (await self.session.execute(client_balances_stmt)).all()]
        narads = [dict(row._mapping) for row in (await self.session.execute(narads_stmt)).all()]
        executors = [dict(row._mapping) for row in (await self.session.execute(executors_stmt)).all()]
        payroll = [dict(row._mapping) for row in (await self.session.execute(payroll_stmt)).all()]
        payroll_operations = [dict(row._mapping) for row in (await self.session.execute(payroll_operations_stmt)).all()]
        materials = [dict(row._mapping) for row in (await self.session.execute(materials_stmt)).all()]
        actual_material_consumption = [
            dict(row._mapping) for row in (await self.session.execute(actual_material_consumption_stmt)).all()
        ]
        narad_material_consumption = [
            dict(row._mapping) for row in (await self.session.execute(narad_material_consumption_stmt)).all()
        ]

        return {
            "summary": {
                "total_narads": int(summary_row.total_narads or 0),
                "open_narads": int(summary_row.open_narads or 0),
                "overdue_narads": int(summary_row.overdue_narads or 0),
                "total_revenue": Decimal(revenue_row.total_revenue or Decimal("0.00")).quantize(TWO_PLACES),
                "total_paid": Decimal(revenue_row.total_paid or Decimal("0.00")).quantize(TWO_PLACES),
                "total_balance_due": Decimal(revenue_row.total_balance_due or Decimal("0.00")).quantize(TWO_PLACES),
                "low_stock_materials": int(low_stock_materials or 0),
                "payroll_total": Decimal(payroll_total or Decimal("0.00")).quantize(TWO_PLACES),
                "actual_material_consumption_total": Decimal(
                    actual_material_consumption_total or Decimal("0.00")
                ).quantize(TWO_PLACES),
            },
            "client_balances": client_balances,
            "narads": narads,
            "executors": executors,
            "payroll": payroll,
            "payroll_operations": payroll_operations,
            "materials": materials,
            "actual_material_consumption": actual_material_consumption,
            "narad_material_consumption": narad_material_consumption,
        }
