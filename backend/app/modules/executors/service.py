from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_executor_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.executor import Executor
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.executors.schemas import ExecutorCreate, ExecutorListResponse, ExecutorRead, ExecutorUpdate


class ExecutorService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService, search: SearchService):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_executors(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
    ) -> ExecutorListResponse:
        search_ids = await self._search.search_executors(search) if search else None
        async with self._uow as uow:
            rows, total_items = await uow.executors.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                active_only=active_only,
                ids=search_ids if search_ids else None,
            )
            items = [
                ExecutorRead.model_validate(executor).model_copy(
                    update={
                        "payment_category_name": executor.payment_category.name if executor.payment_category else None,
                        "work_count": work_count,
                        "production_total": production_total,
                        "earnings_total": earnings_total,
                        "earnings_current_month": earnings_current_month,
                    },
                )
                for executor, work_count, production_total, earnings_total, earnings_current_month in rows
            ]
        return PaginatedResponse[ExecutorRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_executor(self, executor_id: str) -> ExecutorRead:
        async with self._uow as uow:
            rows, _ = await uow.executors.list(page=1, page_size=1, ids=[executor_id])
            if not rows:
                raise NotFoundError("executor", executor_id)
            executor, work_count, production_total, earnings_total, earnings_current_month = rows[0]
            return ExecutorRead.model_validate(executor).model_copy(
                update={
                    "payment_category_name": executor.payment_category.name if executor.payment_category else None,
                    "work_count": work_count,
                    "production_total": production_total,
                    "earnings_total": earnings_total,
                    "earnings_current_month": earnings_current_month,
                }
            )

    async def create_executor(self, payload: ExecutorCreate) -> ExecutorRead:
        async with self._uow as uow:
            executor = await uow.executors.add(Executor(**payload.model_dump()))
            await uow.commit()
        await self._index_executor(executor.id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_executor(executor.id)

    async def update_executor(self, executor_id: str, payload: ExecutorUpdate) -> ExecutorRead:
        async with self._uow as uow:
            executor = await uow.executors.get(executor_id)
            if executor is None:
                raise NotFoundError("executor", executor_id)
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(executor, field, value)
            await uow.commit()
        await self._index_executor(executor.id)
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_executor(executor.id)

    async def archive_executor(self, executor_id: str) -> ExecutorRead:
        return await self.update_executor(executor_id, ExecutorUpdate(is_active=False))

    async def _index_executor(self, executor_id: str) -> None:
        async with self._uow as uow:
            executor = await uow.executors.get(executor_id)
            if executor is None:
                return
        await self._search.index_document(
            settings.elasticsearch_executors_index,
            executor.id,
            build_executor_search_document(executor),
        )
