from __future__ import annotations

from datetime import datetime, timezone

from app.common.payroll_periods import build_payroll_periods_preview, normalize_payroll_period_start_days


def test_normalize_payroll_period_start_days_sorts_unique_values():
    assert normalize_payroll_period_start_days([25, 10, 25, 1]) == [1, 10, 25]


def test_build_payroll_periods_preview_uses_multiple_starts():
    periods = build_payroll_periods_preview(
        [10, 25],
        anchor_at=datetime(2026, 3, 25, 9, 0, tzinfo=timezone.utc),
        count=3,
    )

    assert periods[0]["is_current"] is True
    assert periods[0]["date_from"] == datetime(2026, 3, 25, 0, 0, 0, tzinfo=timezone.utc)
    assert periods[0]["date_to"] == datetime(2026, 4, 9, 23, 59, 59, tzinfo=timezone.utc)
    assert periods[1]["date_from"] == datetime(2026, 3, 10, 0, 0, 0, tzinfo=timezone.utc)
    assert periods[1]["date_to"] == datetime(2026, 3, 24, 23, 59, 59, tzinfo=timezone.utc)
