from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.modules.reports.service import ReportsService


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeReportsRepository:
    snapshot: dict[str, object]

    async def get_snapshot(self, *, date_from: datetime | None, date_to: datetime | None):
        return self.snapshot


class FakeContextUow:
    def __init__(self, snapshot: dict[str, object]):
        self.reports = FakeReportsRepository(snapshot)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.mark.asyncio
async def test_reports_service_builds_snapshot_and_overdue_flags():
    past_deadline = now_utc() - timedelta(days=2)
    snapshot = {
        "summary": {
            "total_narads": 5,
            "open_narads": 2,
            "overdue_narads": 1,
            "total_revenue": Decimal("150000.00"),
            "total_paid": Decimal("95000.00"),
            "total_balance_due": Decimal("55000.00"),
            "low_stock_materials": 3,
            "payroll_total": Decimal("19500.00"),
            "actual_material_consumption_total": Decimal("4200.00"),
        },
        "client_balances": [
            {
                "client_id": "client-1",
                "client_name": "Клиника Улыбка",
                "narads_count": 3,
                "works_count": 7,
                "total_price": Decimal("120000.00"),
                "amount_paid": Decimal("70000.00"),
                "balance_due": Decimal("50000.00"),
                "last_received_at": now_utc(),
            }
        ],
        "narads": [
            {
                "narad_id": "narad-1",
                "narad_number": "N-2026-0001",
                "title": "Комплексное протезирование",
                "client_name": "Клиника Улыбка",
                "doctor_name": "Анна Петрова",
                "patient_name": "Ирина Соколова",
                "status": "new",
                "works_count": 2,
                "total_price": Decimal("55000.00"),
                "total_cost": Decimal("21000.00"),
                "total_margin": Decimal("34000.00"),
                "amount_paid": Decimal("10000.00"),
                "balance_due": Decimal("45000.00"),
                "received_at": now_utc() - timedelta(days=5),
                "deadline_at": past_deadline,
                "completed_at": None,
                "closed_at": None,
            },
            {
                "narad_id": "narad-2",
                "narad_number": "N-2026-0002",
                "title": "Контрольный заказ",
                "client_name": "Клиника Профи",
                "doctor_name": None,
                "patient_name": None,
                "status": "delivered",
                "works_count": 1,
                "total_price": Decimal("12000.00"),
                "total_cost": Decimal("4000.00"),
                "total_margin": Decimal("8000.00"),
                "amount_paid": Decimal("12000.00"),
                "balance_due": Decimal("0.00"),
                "received_at": now_utc() - timedelta(days=4),
                "deadline_at": past_deadline,
                "completed_at": now_utc() - timedelta(days=1),
                "closed_at": now_utc() - timedelta(days=1),
            },
        ],
        "executors": [
            {
                "executor_id": "executor-1",
                "executor_name": "Дмитрий Иванов",
                "active_works": 2,
                "closed_works": 5,
                "revenue_total": Decimal("78000.00"),
                "earnings_total": Decimal("19500.00"),
                "last_closed_at": now_utc() - timedelta(days=1),
            }
        ],
        "materials": [
            {
                "material_id": "material-1",
                "name": "Циркониевый диск",
                "category": "Керамика",
                "unit": "piece",
                "stock": Decimal("12.000"),
                "reserved_stock": Decimal("2.000"),
                "available_stock": Decimal("10.000"),
                "min_stock": Decimal("5.000"),
                "stock_value": Decimal("36000.00"),
                "is_low_stock": False,
            }
        ],
        "payroll": [
            {
                "executor_id": "executor-1",
                "executor_name": "Дмитрий Иванов",
                "narads_count": 3,
                "operations_count": 8,
                "quantity_total": Decimal("10.00"),
                "earnings_total": Decimal("19500.00"),
                "last_closed_at": now_utc() - timedelta(days=1),
            }
        ],
        "payroll_operations": [
            {
                "executor_id": "executor-1",
                "executor_name": "Дмитрий Иванов",
                "operation_code": "MILL",
                "operation_name": "Фрезеровка",
                "narads_count": 2,
                "operations_count": 3,
                "quantity_total": Decimal("4.00"),
                "earnings_total": Decimal("7200.00"),
                "last_closed_at": now_utc() - timedelta(days=1),
            }
        ],
        "actual_material_consumption": [
            {
                "movement_id": "movement-1",
                "movement_date": now_utc() - timedelta(days=1),
                "material_id": "material-1",
                "material_name": "Циркониевый диск",
                "material_category": "Керамика",
                "unit": "piece",
                "quantity": Decimal("1.000"),
                "unit_cost": Decimal("4200.00"),
                "total_cost": Decimal("4200.00"),
                "balance_after": Decimal("11.000"),
                "reason": "Выдача технику на неделю",
            }
        ],
        "narad_material_consumption": [
            {
                "movement_id": "movement-2",
                "movement_date": now_utc() - timedelta(days=1),
                "narad_id": "narad-1",
                "narad_number": "N-2026-0001",
                "narad_title": "Комплексное протезирование",
                "client_name": "Клиника Улыбка",
                "work_id": "work-1",
                "work_order_number": "DL-2026-0001",
                "material_id": "material-1",
                "material_name": "Циркониевый диск",
                "material_category": "Керамика",
                "unit": "piece",
                "quantity": Decimal("1.000"),
                "unit_cost": Decimal("4200.00"),
                "total_cost": Decimal("4200.00"),
                "balance_after": Decimal("10.000"),
                "reason": "Списание при закрытии наряда N-2026-0001 / заказ DL-2026-0001",
            }
        ],
    }

    service = ReportsService(uow=FakeContextUow(snapshot))

    result = await service.get_snapshot(date_from=None, date_to=None)

    assert result.summary.total_narads == 5
    assert result.summary.total_balance_due == Decimal("55000.00")
    assert result.client_balances[0].client_name == "Клиника Улыбка"
    assert result.narads[0].is_overdue is True
    assert result.narads[1].is_overdue is False
    assert result.executors[0].earnings_total == Decimal("19500.00")
    assert result.summary.payroll_total == Decimal("19500.00")
    assert result.payroll[0].operations_count == 8
    assert result.payroll_operations[0].operation_name == "Фрезеровка"
    assert result.materials[0].available_stock == Decimal("10.000")
    assert result.actual_material_consumption[0].reason == "Выдача технику на неделю"
    assert result.narad_material_consumption[0].narad_number == "N-2026-0001"
