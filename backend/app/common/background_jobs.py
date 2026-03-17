from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.common.search_documents import (
    build_client_search_document,
    build_doctor_search_document,
    build_executor_search_document,
    build_material_search_document,
    build_operation_search_document,
    build_work_catalog_search_document,
    build_work_search_document,
)
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.dashboard.service import DashboardService


logger = logging.getLogger(__name__)


class BackgroundJobService:
    def __init__(
        self,
        *,
        uow_factory: Callable[[], SQLAlchemyUnitOfWork],
        search: SearchService,
        cache: CacheService,
        dashboard_service_factory: Optional[Callable[[], DashboardService]] = None,
    ):
        self._uow_factory = uow_factory
        self._search = search
        self._cache = cache
        self._dashboard_service_factory = dashboard_service_factory or (
            lambda: DashboardService(self._uow_factory(), self._cache)
        )

    async def reindex_search_documents(self, *, batch_size: Optional[int] = None) -> dict[str, int]:
        resolved_batch_size = batch_size or settings.search_reindex_batch_size
        await self._search.prepare_index(
            settings.elasticsearch_clients_index,
            SearchService.clients_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_doctors_index,
            SearchService.doctors_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_executors_index,
            SearchService.executors_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_materials_index,
            SearchService.materials_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_operations_index,
            SearchService.operations_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_work_catalog_index,
            SearchService.work_catalog_index_mappings(),
            purge=True,
        )
        await self._search.prepare_index(
            settings.elasticsearch_works_index,
            SearchService.works_index_mappings(),
            purge=True,
        )

        counts = {
            "clients": await self._reindex_clients(resolved_batch_size),
            "doctors": await self._reindex_doctors(resolved_batch_size),
            "executors": await self._reindex_executors(resolved_batch_size),
            "materials": await self._reindex_materials(resolved_batch_size),
            "operations": await self._reindex_operations(resolved_batch_size),
            "work_catalog": await self._reindex_work_catalog(resolved_batch_size),
            "works": await self._reindex_works(resolved_batch_size),
        }

        await self._search.refresh_index(settings.elasticsearch_clients_index)
        await self._search.refresh_index(settings.elasticsearch_doctors_index)
        await self._search.refresh_index(settings.elasticsearch_executors_index)
        await self._search.refresh_index(settings.elasticsearch_materials_index)
        await self._search.refresh_index(settings.elasticsearch_operations_index)
        await self._search.refresh_index(settings.elasticsearch_work_catalog_index)
        await self._search.refresh_index(settings.elasticsearch_works_index)
        return counts

    async def refresh_dashboard_cache(self, *, windows: Optional[Sequence[str]] = None) -> list[str]:
        await self._cache.invalidate_prefix("dashboard:")
        dashboard_service = self._dashboard_service_factory()
        warmed_windows: list[str] = []

        for window in windows or settings.parsed_dashboard_cache_windows:
            date_from, date_to = self._resolve_dashboard_window(window)
            await dashboard_service.get_overview(date_from=date_from, date_to=date_to)
            warmed_windows.append(window)

        return warmed_windows

    async def _reindex_clients(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_clients_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_clients_batch,
            build_document=lambda client: (client.id, build_client_search_document(client)),
        )

    async def _reindex_executors(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_executors_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_executors_batch,
            build_document=lambda executor: (executor.id, build_executor_search_document(executor)),
        )

    async def _reindex_doctors(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_doctors_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_doctors_batch,
            build_document=lambda doctor: (doctor.id, build_doctor_search_document(doctor)),
        )

    async def _reindex_materials(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_materials_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_materials_batch,
            build_document=lambda material: (material.id, build_material_search_document(material)),
        )

    async def _reindex_works(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_works_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_works_batch,
            build_document=lambda work: (work.id, build_work_search_document(work)),
        )

    async def _reindex_operations(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_operations_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_operations_batch,
            build_document=lambda operation: (operation.id, build_operation_search_document(operation)),
        )

    async def _reindex_work_catalog(self, batch_size: int) -> int:
        return await self._reindex_entities(
            index_name=settings.elasticsearch_work_catalog_index,
            batch_size=batch_size,
            fetch_batch=self._fetch_work_catalog_batch,
            build_document=lambda item: (item.id, build_work_catalog_search_document(item)),
        )

    async def _reindex_entities(
        self,
        *,
        index_name: str,
        batch_size: int,
        fetch_batch: Callable[[int, int], Awaitable[list[Any]]],
        build_document: Callable[[Any], tuple[str, dict[str, Any]]],
    ) -> int:
        offset = 0
        processed = 0

        while True:
            batch = await fetch_batch(offset, batch_size)
            if not batch:
                break
            await self._search.bulk_index_documents(
                index_name,
                [build_document(entity) for entity in batch],
                refresh=False,
            )
            processed += len(batch)
            offset += len(batch)

        return processed

    async def _fetch_clients_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.clients.list_for_indexing(offset=offset, limit=limit)

    async def _fetch_executors_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.executors.list_for_indexing(offset=offset, limit=limit)

    async def _fetch_doctors_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.doctors.list_for_indexing(offset=offset, limit=limit)

    async def _fetch_materials_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.materials.list_for_indexing(offset=offset, limit=limit)

    async def _fetch_works_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.works.list_for_indexing(offset=offset, limit=limit)

    async def _fetch_operations_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.operations.list_operations_for_indexing(offset=offset, limit=limit)

    async def _fetch_work_catalog_batch(self, offset: int, limit: int) -> list[Any]:
        async with self._uow_factory() as uow:
            return await uow.work_catalog.list_for_indexing(offset=offset, limit=limit)

    def _resolve_dashboard_window(self, window: str) -> tuple[Optional[datetime], Optional[datetime]]:
        normalized = window.strip().lower()
        if normalized in {"all", "default"}:
            return None, None

        if normalized.endswith("d") and normalized[:-1].isdigit():
            days = int(normalized[:-1])
            date_to = datetime.now(timezone.utc).replace(microsecond=0)
            return date_to - timedelta(days=days), date_to

        raise ValueError(f"Unsupported dashboard cache window: {window}")


class BackgroundJobRunner:
    def __init__(self, *, service: BackgroundJobService, cache: CacheService):
        self._service = service
        self._cache = cache
        self._tasks: list[asyncio.Task[None]] = []

    def start(self) -> None:
        if not settings.background_jobs_enabled:
            logger.info("Background jobs are disabled.")
            return

        self._register_job(
            name="search_reindex",
            interval_seconds=settings.search_reindex_interval_seconds,
            lock_key="locks:jobs:search_reindex",
            job=self._run_search_reindex,
        )
        self._register_job(
            name="dashboard_cache_refresh",
            interval_seconds=settings.dashboard_cache_refresh_interval_seconds,
            lock_key="locks:jobs:dashboard_cache_refresh",
            job=self._run_dashboard_cache_refresh,
        )

    async def stop(self) -> None:
        if not self._tasks:
            return

        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    def _register_job(
        self,
        *,
        name: str,
        interval_seconds: int,
        lock_key: str,
        job: Callable[[], Awaitable[None]],
    ) -> None:
        if interval_seconds <= 0:
            logger.info("Background job %s is disabled by interval=%s.", name, interval_seconds)
            return

        self._tasks.append(
            asyncio.create_task(
                self._run_periodic_job(
                    name=name,
                    interval_seconds=interval_seconds,
                    lock_key=lock_key,
                    job=job,
                )
            )
        )

    async def _run_periodic_job(
        self,
        *,
        name: str,
        interval_seconds: int,
        lock_key: str,
        job: Callable[[], Awaitable[None]],
    ) -> None:
        await asyncio.sleep(max(settings.background_job_startup_delay_seconds, 0))

        while True:
            token: Optional[str] = None
            try:
                token = await self._cache.acquire_lock(lock_key, ttl_seconds=settings.background_job_lock_ttl_seconds)
                if token:
                    await job()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Background job %s failed.", name)
            finally:
                if token:
                    await self._cache.release_lock(lock_key, token)
            await asyncio.sleep(interval_seconds)

    async def _run_search_reindex(self) -> None:
        counts = await self._service.reindex_search_documents()
        logger.info("Search reindex completed: %s", counts)

    async def _run_dashboard_cache_refresh(self) -> None:
        windows = await self._service.refresh_dashboard_cache()
        logger.info("Dashboard cache refresh completed for windows: %s", windows)
