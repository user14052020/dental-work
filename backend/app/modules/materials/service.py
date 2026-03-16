from __future__ import annotations

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_material_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.material import Material
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.materials.schemas import (
    MaterialConsume,
    MaterialCreate,
    MaterialListResponse,
    MaterialRead,
    MaterialUpdate,
)


class MaterialService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService, search: SearchService):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_materials(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        low_stock_only: bool,
    ) -> MaterialListResponse:
        search_ids = await self._search.search_materials(search) if search else None
        async with self._uow as uow:
            materials, total_items = await uow.materials.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                low_stock_only=low_stock_only,
                ids=search_ids if search_ids else None,
            )
            items = [
                MaterialRead.model_validate(material).model_copy(
                    update={"is_low_stock": material.stock <= material.min_stock}
                )
                for material in materials
            ]
        return PaginatedResponse[MaterialRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_material(self, material_id: str) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.get(material_id)
            if material is None:
                raise NotFoundError("material", material_id)
            return MaterialRead.model_validate(material).model_copy(
                update={"is_low_stock": material.stock <= material.min_stock}
            )

    async def create_material(self, payload: MaterialCreate) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.add(Material(**payload.model_dump()))
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return MaterialRead.model_validate(material).model_copy(
            update={"is_low_stock": material.stock <= material.min_stock}
        )

    async def update_material(self, material_id: str, payload: MaterialUpdate) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.get(material_id)
            if material is None:
                raise NotFoundError("material", material_id)
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(material, field, value)
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return MaterialRead.model_validate(material).model_copy(
            update={"is_low_stock": material.stock <= material.min_stock}
        )

    async def consume_material(self, material_id: str, payload: MaterialConsume) -> MaterialRead:
        async with self._uow as uow:
            material = await uow.materials.consume_stock(material_id, payload.quantity)
            await uow.commit()
        await self._index_material(material)
        await self._cache.invalidate_prefix("dashboard:")
        return MaterialRead.model_validate(material).model_copy(
            update={"is_low_stock": material.stock <= material.min_stock}
        )

    async def _index_material(self, material: Material) -> None:
        await self._search.index_document(
            settings.elasticsearch_materials_index,
            material.id,
            build_material_search_document(material),
        )
