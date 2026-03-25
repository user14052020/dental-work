from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta, timezone


DEFAULT_PAYROLL_PERIOD_START_DAYS = [1]
PAYROLL_PERIODS_PREVIEW_COUNT = 6


def normalize_payroll_period_start_days(days: list[int] | None) -> list[int]:
    values = days or DEFAULT_PAYROLL_PERIOD_START_DAYS
    normalized = sorted(
        {
            day
            for day in (
                int(value)
                for value in values
                if value is not None and 1 <= int(value) <= 31
            )
        }
    )
    return normalized or DEFAULT_PAYROLL_PERIOD_START_DAYS.copy()


def build_payroll_periods_preview(
    days: list[int] | None,
    *,
    anchor_at: datetime | None = None,
    count: int = PAYROLL_PERIODS_PREVIEW_COUNT,
) -> list[dict[str, object]]:
    normalized_days = normalize_payroll_period_start_days(days)
    anchor_date = (anchor_at or datetime.now(timezone.utc)).astimezone(timezone.utc).date()
    boundaries = _build_period_boundaries(normalized_days, anchor_date, count=count)
    current_index = max(index for index, boundary in enumerate(boundaries) if boundary <= anchor_date)

    periods: list[dict[str, object]] = []
    for index in range(current_index, max(current_index - count, -1), -1):
        if index + 1 >= len(boundaries):
            continue
        period_start = boundaries[index]
        period_end = boundaries[index + 1] - timedelta(days=1)
        offset = current_index - index
        label = f"{period_start:%d.%m.%Y} - {period_end:%d.%m.%Y}"
        periods.append(
            {
                "key": f"payroll-period-{offset}",
                "label": f"Текущий: {label}" if offset == 0 else label,
                "date_from": datetime.combine(period_start, time(0, 0, 0), tzinfo=timezone.utc),
                "date_to": datetime.combine(period_end, time(23, 59, 59), tzinfo=timezone.utc),
                "is_current": offset == 0,
            }
        )
    return periods


def _build_period_boundaries(days: list[int], anchor_date: date, *, count: int) -> list[date]:
    boundaries: set[date] = set()
    months_back = max(count + 4, 8)
    months_forward = 3
    for month_offset in range(-months_back, months_forward + 1):
        year, month = _shift_month(anchor_date.year, anchor_date.month, month_offset)
        for day in days:
            boundaries.add(date(year, month, min(day, calendar.monthrange(year, month)[1])))
    return sorted(boundaries)


def _shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    month_index = year * 12 + (month - 1) + offset
    shifted_year = month_index // 12
    shifted_month = month_index % 12 + 1
    return shifted_year, shifted_month
