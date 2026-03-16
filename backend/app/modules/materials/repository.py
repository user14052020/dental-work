from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.material import Material


class MaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, material: Material) -> Material:
        self.session.add(material)
        await self.session.flush()
        return material

    async def get(self, material_id: str) -> Material | None:
        result = await self.session.execute(select(Material).where(Material.id == material_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        low_stock_only: bool,
        ids: list[str] | None = None,
    ) -> tuple[list[Material], int]:
        stmt: Select = select(Material).order_by(Material.created_at.desc())
        count_stmt = select(func.count(Material.id))

        if search:
            filter_expression = or_(
                Material.name.ilike(f"%{search}%"),
                Material.category.ilike(f"%{search}%"),
                Material.unit.ilike(f"%{search}%"),
                Material.supplier.ilike(f"%{search}%"),
                Material.comment.ilike(f"%{search}%"),
            )
            stmt = stmt.where(filter_expression)
            count_stmt = count_stmt.where(filter_expression)

        if low_stock_only:
            low_stock_filter = Material.stock <= Material.min_stock
            stmt = stmt.where(low_stock_filter)
            count_stmt = count_stmt.where(low_stock_filter)

        if ids:
            stmt = stmt.where(Material.id.in_(ids))
            count_stmt = count_stmt.where(Material.id.in_(ids))

        result = await self.session.execute(stmt.offset((page - 1) * page_size).limit(page_size))
        total_items = await self.session.scalar(count_stmt)
        return list(result.scalars().all()), int(total_items or 0)

    async def list_by_ids(self, ids: list[str]) -> list[Material]:
        if not ids:
            return []
        result = await self.session.execute(select(Material).where(Material.id.in_(ids)))
        return list(result.scalars().all())

    async def list_for_indexing(self, *, offset: int, limit: int) -> list[Material]:
        result = await self.session.execute(
            select(Material).order_by(Material.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def consume_stock(self, material_id: str, quantity: Decimal) -> Material:
        material = await self.get(material_id)
        if material is None:
            raise NotFoundError("material", material_id)
        if material.stock < quantity:
            raise ConflictError(
                "Material stock is insufficient for this operation.",
                code="insufficient_material_stock",
                details={"material_id": material_id, "requested": str(quantity), "available": str(material.stock)},
            )
        material.stock -= quantity
        await self.session.flush()
        return material
