from __future__ import annotations

from datetime import datetime, timezone

from app.common.services import CacheService
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.dashboard.schemas import DashboardRead, DashboardTopItem


class DashboardService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService):
        self._uow = uow
        self._cache = cache

    async def get_overview(self, *, date_from: datetime | None, date_to: datetime | None) -> DashboardRead:
        cache_key = f"dashboard:{date_from}:{date_to}"
        cached = await self._cache.get_json(cache_key)
        if cached:
            return DashboardRead.model_validate(cached)

        async with self._uow as uow:
            overview = await uow.dashboard.get_overview(date_from=date_from, date_to=date_to)

        payload = DashboardRead(
            active_works=overview["active_works"],
            overdue_works=overview["overdue_works"],
            revenue=overview["revenue"],
            profit=overview["profit"],
            material_expenses=overview["material_expenses"],
            top_clients=[DashboardTopItem.model_validate(item) for item in overview["top_clients"]],
            top_executors=[DashboardTopItem.model_validate(item) for item in overview["top_executors"]],
            generated_at=datetime.now(timezone.utc),
        )
        await self._cache.set_json(cache_key, payload.model_dump(mode="json"), ttl_seconds=120)
        return payload
