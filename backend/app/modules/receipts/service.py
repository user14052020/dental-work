from __future__ import annotations

from decimal import Decimal

from app.common.pagination import PaginatedResponse
from app.common.enums import StockMovementType
from app.common.search_documents import build_material_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models.material_receipt import MaterialReceipt, MaterialReceiptItem
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.receipts.schemas import (
    MaterialReceiptCompactRead,
    MaterialReceiptCreate,
    MaterialReceiptItemRead,
    MaterialReceiptListResponse,
    MaterialReceiptRead,
)


THREE_PLACES = Decimal("0.001")
TWO_PLACES = Decimal("0.01")


class MaterialReceiptService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, cache: CacheService, search: SearchService):
        self._uow = uow
        self._cache = cache
        self._search = search

    async def list_receipts(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        supplier: str | None,
        date_from,
        date_to,
    ) -> MaterialReceiptListResponse:
        async with self._uow as uow:
            receipts, total_items = await uow.receipts.list(
                page=page,
                page_size=page_size,
                search=search,
                supplier=supplier,
                date_from=date_from,
                date_to=date_to,
            )
            items = [self._map_receipt_compact(receipt) for receipt in receipts]
        return PaginatedResponse[MaterialReceiptCompactRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_receipt(self, receipt_id: str) -> MaterialReceiptRead:
        async with self._uow as uow:
            receipt = await uow.receipts.get(receipt_id)
            if receipt is None:
                raise NotFoundError("material_receipt", receipt_id)
            return self._map_receipt_detail(receipt)

    async def create_receipt(self, payload: MaterialReceiptCreate) -> MaterialReceiptRead:
        async with self._uow as uow:
            existing = await uow.receipts.get_by_number(payload.receipt_number)
            if existing is not None:
                raise ConflictError("Receipt number already exists.", code="receipt_number_exists")

            material_ids = [item.material_id for item in payload.items]
            materials = {material.id: material for material in await uow.materials.list_by_ids(material_ids)}

            receipt = await uow.receipts.add(
                MaterialReceipt(
                    receipt_number=payload.receipt_number,
                    received_at=payload.received_at,
                    supplier=payload.supplier,
                    comment=payload.comment,
                )
            )

            touched_materials = []
            for index, item in enumerate(payload.items):
                material = materials.get(item.material_id)
                if material is None:
                    raise NotFoundError("material", item.material_id)

                quantity = item.quantity.quantize(THREE_PLACES)
                unit_price = item.unit_price.quantize(TWO_PLACES)
                total_price = (quantity * unit_price).quantize(TWO_PLACES)
                previous_stock = material.stock
                previous_value = (material.average_price * previous_stock).quantize(TWO_PLACES)
                next_stock = (previous_stock + quantity).quantize(THREE_PLACES)
                next_value = (previous_value + total_price).quantize(TWO_PLACES)
                next_average_price = (next_value / next_stock).quantize(TWO_PLACES) if next_stock > 0 else unit_price

                material.purchase_price = unit_price
                material.average_price = next_average_price
                if payload.supplier:
                    material.supplier = payload.supplier

                receipt_item = await uow.receipts.add_item(
                    MaterialReceiptItem(
                        receipt_id=receipt.id,
                        material_id=material.id,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        sort_order=index,
                    )
                )
                receipt_item.material = material
                await uow.materials.change_stock(
                    material.id,
                    quantity_delta=quantity,
                    movement_type=StockMovementType.RECEIPT.value,
                    unit_cost=unit_price,
                    comment=f"Приход {receipt.receipt_number}",
                    receipt_id=receipt.id,
                )
                touched_materials.append(material)

            await uow.commit()

        for material in touched_materials:
            await self._search.index_document(
                settings.elasticsearch_materials_index,
                material.id,
                build_material_search_document(material),
            )
        await self._cache.invalidate_prefix("dashboard:")
        return await self.get_receipt(receipt.id)

    @staticmethod
    def _map_receipt_compact(receipt: MaterialReceipt) -> MaterialReceiptCompactRead:
        total_amount = sum((item.total_price for item in receipt.items), Decimal("0.00")).quantize(TWO_PLACES)
        total_quantity = sum((item.quantity for item in receipt.items), Decimal("0.000")).quantize(THREE_PLACES)
        return MaterialReceiptCompactRead(
            id=receipt.id,
            created_at=receipt.created_at,
            updated_at=receipt.updated_at,
            receipt_number=receipt.receipt_number,
            received_at=receipt.received_at,
            supplier=receipt.supplier,
            items_count=len(receipt.items),
            total_amount=total_amount,
            total_quantity=total_quantity,
        )

    def _map_receipt_detail(self, receipt: MaterialReceipt) -> MaterialReceiptRead:
        compact = self._map_receipt_compact(receipt)
        items = [
            MaterialReceiptItemRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                material_id=item.material_id,
                material_name=item.material.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                sort_order=item.sort_order,
            )
            for item in sorted(receipt.items, key=lambda row: row.sort_order)
        ]
        return MaterialReceiptRead(**compact.model_dump(), comment=receipt.comment, items=items)
