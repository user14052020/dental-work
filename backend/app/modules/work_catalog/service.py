from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_work_catalog_search_document
from app.common.services import SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.work_catalog import WorkCatalogItem, WorkCatalogItemOperation
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.work_catalog.schemas import (
    WorkCatalogItemCreate,
    WorkCatalogItemListResponse,
    WorkCatalogItemRead,
    WorkCatalogItemUpdate,
    WorkCatalogTemplateOperationRead,
)


class WorkCatalogService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService):
        self._uow = uow
        self._search = search

    async def list_items(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
        category: str | None,
    ) -> WorkCatalogItemListResponse:
        search_ids = await self._search.search_work_catalog(search) if search else None
        async with self._uow as uow:
            items, total_items = await uow.work_catalog.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                active_only=active_only,
                category=category,
                ids=search_ids if search_ids else None,
            )
            rows = [self._map_item(item) for item in items]
        return PaginatedResponse[WorkCatalogItemRead].create(
            rows,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    async def get_item(self, item_id: str) -> WorkCatalogItemRead:
        async with self._uow as uow:
            item = await uow.work_catalog.get(item_id)
            if item is None:
                raise NotFoundError("work_catalog_item", item_id)
            return self._map_item(item)

    async def create_item(self, payload: WorkCatalogItemCreate) -> WorkCatalogItemRead:
        async with self._uow as uow:
            if await uow.work_catalog.get_by_code(payload.code):
                raise ConflictError("Work catalog code already exists.", code="work_catalog_code_exists")
            item = WorkCatalogItem(
                code=payload.code,
                name=payload.name,
                category=payload.category,
                description=payload.description,
                base_price=payload.base_price,
                default_duration_hours=payload.default_duration_hours,
                is_active=payload.is_active,
                sort_order=payload.sort_order,
            )
            item.default_operations = await self._build_default_operations(uow, payload.default_operations)
            item = await uow.work_catalog.add(item)
            await uow.commit()
        await self._search.index_document(
            settings.elasticsearch_work_catalog_index,
            item.id,
            build_work_catalog_search_document(item),
        )
        return await self.get_item(item.id)

    async def update_item(self, item_id: str, payload: WorkCatalogItemUpdate) -> WorkCatalogItemRead:
        async with self._uow as uow:
            item = await uow.work_catalog.get(item_id)
            if item is None:
                raise NotFoundError("work_catalog_item", item_id)
            data = payload.model_dump(exclude_unset=True)
            if "code" in data and data["code"] != item.code:
                existing = await uow.work_catalog.get_by_code(data["code"])
                if existing is not None and existing.id != item_id:
                    raise ConflictError("Work catalog code already exists.", code="work_catalog_code_exists")
            for field in [
                "code",
                "name",
                "category",
                "description",
                "base_price",
                "default_duration_hours",
                "is_active",
                "sort_order",
            ]:
                if field in data:
                    setattr(item, field, data[field])
            if payload.default_operations is not None:
                item.default_operations = await self._build_default_operations(uow, payload.default_operations)
            await uow.commit()
        await self._search.index_document(
            settings.elasticsearch_work_catalog_index,
            item.id,
            build_work_catalog_search_document(item),
        )
        return await self.get_item(item_id)

    async def _build_default_operations(self, uow: SQLAlchemyUnitOfWork, rows: list) -> list[WorkCatalogItemOperation]:
        operation_ids = [row.operation_id for row in rows]
        operations = {item.id: item for item in await uow.operations.list_operations_by_ids(operation_ids)}
        built: list[WorkCatalogItemOperation] = []
        for row in rows:
            operation = operations.get(row.operation_id)
            if operation is None:
                raise NotFoundError("operation", row.operation_id)
            built.append(
                WorkCatalogItemOperation(
                    operation_id=operation.id,
                    quantity=row.quantity,
                    note=row.note,
                    sort_order=row.sort_order,
                )
            )
        return built

    @staticmethod
    def _map_item(item: WorkCatalogItem) -> WorkCatalogItemRead:
        return WorkCatalogItemRead(
            id=item.id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            code=item.code,
            name=item.name,
            category=item.category,
            description=item.description,
            base_price=item.base_price,
            default_duration_hours=item.default_duration_hours,
            is_active=item.is_active,
            sort_order=item.sort_order,
            default_operations=[
                WorkCatalogTemplateOperationRead(
                    id=operation.id,
                    created_at=operation.created_at,
                    updated_at=operation.updated_at,
                    operation_id=operation.operation_id,
                    operation_code=operation.operation.code,
                    operation_name=operation.operation.name,
                    quantity=operation.quantity,
                    note=operation.note,
                    sort_order=operation.sort_order,
                )
                for operation in sorted(item.default_operations, key=lambda entry: entry.sort_order)
                if operation.operation is not None
            ],
        )
