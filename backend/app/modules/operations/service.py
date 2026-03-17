from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_operation_search_document
from app.common.services import SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.operation import ExecutorCategory, OperationCatalog, OperationCategoryRate
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.operations.schemas import (
    ExecutorCategoryCreate,
    ExecutorCategoryListResponse,
    ExecutorCategoryRead,
    ExecutorCategoryUpdate,
    OperationCatalogCreate,
    OperationCatalogListResponse,
    OperationCatalogRead,
    OperationCatalogUpdate,
)


class OperationService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService):
        self._uow = uow
        self._search = search

    async def list_categories(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
    ) -> ExecutorCategoryListResponse:
        async with self._uow as uow:
            items, total_items = await uow.operations.list_categories(
                page=page,
                page_size=page_size,
                search=search,
                active_only=active_only,
            )
            rows = [ExecutorCategoryRead.model_validate(item) for item in items]
        return PaginatedResponse[ExecutorCategoryRead].create(
            rows,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    async def get_category(self, category_id: str) -> ExecutorCategoryRead:
        async with self._uow as uow:
            category = await uow.operations.get_category(category_id)
            if category is None:
                raise NotFoundError("executor_category", category_id)
            return ExecutorCategoryRead.model_validate(category)

    async def create_category(self, payload: ExecutorCategoryCreate) -> ExecutorCategoryRead:
        async with self._uow as uow:
            if await uow.operations.get_category_by_code(payload.code):
                raise ConflictError("Executor category code already exists.", code="executor_category_code_exists")
            category = await uow.operations.add_category(ExecutorCategory(**payload.model_dump()))
            await uow.commit()
            return ExecutorCategoryRead.model_validate(category)

    async def update_category(self, category_id: str, payload: ExecutorCategoryUpdate) -> ExecutorCategoryRead:
        async with self._uow as uow:
            category = await uow.operations.get_category(category_id)
            if category is None:
                raise NotFoundError("executor_category", category_id)
            data = payload.model_dump(exclude_unset=True)
            if "code" in data and data["code"] != category.code:
                existing = await uow.operations.get_category_by_code(data["code"])
                if existing is not None and existing.id != category_id:
                    raise ConflictError("Executor category code already exists.", code="executor_category_code_exists")
            for field, value in data.items():
                setattr(category, field, value)
            await uow.commit()
            return ExecutorCategoryRead.model_validate(category)

    async def list_operations(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        active_only: bool | None,
    ) -> OperationCatalogListResponse:
        search_ids = await self._search.search_operations(search) if search else None
        async with self._uow as uow:
            items, total_items = await uow.operations.list_operations(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                active_only=active_only,
                ids=search_ids if search_ids else None,
            )
            rows = [self._map_operation(item) for item in items]
        return PaginatedResponse[OperationCatalogRead].create(
            rows,
            page=page,
            page_size=page_size,
            total_items=total_items,
        )

    async def get_operation(self, operation_id: str) -> OperationCatalogRead:
        async with self._uow as uow:
            operation = await uow.operations.get_operation(operation_id)
            if operation is None:
                raise NotFoundError("operation", operation_id)
            return self._map_operation(operation)

    async def create_operation(self, payload: OperationCatalogCreate) -> OperationCatalogRead:
        async with self._uow as uow:
            if await uow.operations.get_operation_by_code(payload.code):
                raise ConflictError("Operation code already exists.", code="operation_code_exists")
            operation = OperationCatalog(
                code=payload.code,
                name=payload.name,
                operation_group=payload.operation_group,
                description=payload.description,
                default_quantity=payload.default_quantity,
                default_duration_hours=payload.default_duration_hours,
                is_active=payload.is_active,
                sort_order=payload.sort_order,
            )
            operation.payment_rates = await self._build_rates(uow, payload.rates)
            operation = await uow.operations.add_operation(operation)
            await uow.commit()
        await self._index_operation(operation.id)
        return await self.get_operation(operation.id)

    async def update_operation(self, operation_id: str, payload: OperationCatalogUpdate) -> OperationCatalogRead:
        async with self._uow as uow:
            operation = await uow.operations.get_operation(operation_id)
            if operation is None:
                raise NotFoundError("operation", operation_id)
            data = payload.model_dump(exclude_unset=True)
            if "code" in data and data["code"] != operation.code:
                existing = await uow.operations.get_operation_by_code(data["code"])
                if existing is not None and existing.id != operation_id:
                    raise ConflictError("Operation code already exists.", code="operation_code_exists")
            for field in [
                "code",
                "name",
                "operation_group",
                "description",
                "default_quantity",
                "default_duration_hours",
                "is_active",
                "sort_order",
            ]:
                if field in data:
                    setattr(operation, field, data[field])
            if payload.rates is not None:
                operation.payment_rates = await self._build_rates(uow, payload.rates)
            await uow.commit()
        await self._index_operation(operation_id)
        return await self.get_operation(operation_id)

    async def _build_rates(self, uow: SQLAlchemyUnitOfWork, rates: list) -> list[OperationCategoryRate]:
        category_ids = [item.executor_category_id for item in rates]
        categories = {item.id: item for item in await uow.operations.list_categories_by_ids(category_ids)}
        built_rates: list[OperationCategoryRate] = []
        for item in rates:
            category = categories.get(item.executor_category_id)
            if category is None:
                raise NotFoundError("executor_category", item.executor_category_id)
            built_rates.append(
                OperationCategoryRate(
                    executor_category_id=category.id,
                    labor_rate=item.labor_rate,
                )
            )
        return built_rates

    async def _index_operation(self, operation_id: str) -> None:
        async with self._uow as uow:
            operation = await uow.operations.get_operation(operation_id)
            if operation is None:
                return
        await self._search.index_document(
            settings.elasticsearch_operations_index,
            operation.id,
            build_operation_search_document(operation),
        )

    @staticmethod
    def _map_operation(operation: OperationCatalog) -> OperationCatalogRead:
        return OperationCatalogRead(
            id=operation.id,
            created_at=operation.created_at,
            updated_at=operation.updated_at,
            code=operation.code,
            name=operation.name,
            operation_group=operation.operation_group,
            description=operation.description,
            default_quantity=operation.default_quantity,
            default_duration_hours=operation.default_duration_hours,
            is_active=operation.is_active,
            sort_order=operation.sort_order,
            rates=[
                {
                    "id": rate.id,
                    "created_at": rate.created_at,
                    "updated_at": rate.updated_at,
                    "executor_category_id": rate.executor_category_id,
                    "executor_category_code": rate.executor_category.code,
                    "executor_category_name": rate.executor_category.name,
                    "labor_rate": rate.labor_rate,
                }
                for rate in operation.payment_rates
            ],
        )
