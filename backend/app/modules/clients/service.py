from __future__ import annotations

from decimal import Decimal

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_client_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.client import Client
from app.db.models.client_work_catalog_price import ClientWorkCatalogPrice
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.clients.schemas import (
    ClientCreate,
    ClientDetailRead,
    ClientListResponse,
    ClientRead,
    ClientUpdate,
    ClientWorkCatalogPriceRead,
    ClientWorkCatalogPriceUpsert,
)
from app.modules.works.schemas import WorkCompactRead


class ClientService:
    def __init__(self, uow: SQLAlchemyUnitOfWork, search: SearchService, cache: CacheService):
        self._uow = uow
        self._search = search
        self._cache = cache

    async def list_clients(self, *, page: int, page_size: int, search: str | None) -> ClientListResponse:
        search_ids = await self._search.search_clients(search) if search else None
        async with self._uow as uow:
            rows, total_items = await uow.clients.list(
                page=page,
                page_size=page_size,
                search=search if not search_ids else None,
                ids=search_ids if search_ids else None,
            )
            items = [
                ClientRead.model_validate(client).model_copy(
                    update={
                        "work_count": work_count,
                        "order_total": order_total,
                        "paid_total": paid_total,
                        "unpaid_total": order_total - paid_total,
                    },
                )
                for client, work_count, order_total, paid_total in rows
            ]
        return PaginatedResponse[ClientRead].create(
            items, page=page, page_size=page_size, total_items=total_items
        )

    async def get_client(self, client_id: str) -> ClientDetailRead:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)
            order_total = sum((work.price_for_client for work in client.works), Decimal("0.00"))
            paid_total = sum((work.amount_paid for work in client.works), Decimal("0.00"))
            recent_works = [WorkCompactRead.model_validate(work) for work in client.works[:10]]
            return ClientDetailRead.model_validate(client).model_copy(
                update={
                    "work_count": len(client.works),
                    "order_total": order_total,
                    "paid_total": paid_total,
                    "unpaid_total": order_total - paid_total,
                    "recent_works": recent_works,
                    "work_catalog_prices": self._map_catalog_prices(client.catalog_prices),
                },
            )

    async def create_client(self, payload: ClientCreate) -> ClientRead:
        async with self._uow as uow:
            payload_data = payload.model_dump(exclude={"work_catalog_prices"})
            client = Client(**payload_data)
            client.catalog_prices = await self._build_catalog_prices(uow, payload.work_catalog_prices)
            client = await uow.clients.add(client)
            await uow.commit()
        await self._search.index_document(settings.elasticsearch_clients_index, client.id, build_client_search_document(client))
        await self._cache.invalidate_prefix("dashboard:")
        return ClientRead.model_validate(client)

    async def update_client(self, client_id: str, payload: ClientUpdate) -> ClientRead:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)
            data = payload.model_dump(exclude_unset=True, exclude={"work_catalog_prices"})
            for field, value in data.items():
                setattr(client, field, value)
            if payload.work_catalog_prices is not None:
                client.catalog_prices = await self._build_catalog_prices(uow, payload.work_catalog_prices)
            await uow.commit()
        await self._search.index_document(settings.elasticsearch_clients_index, client.id, build_client_search_document(client))
        await self._cache.invalidate_prefix("dashboard:")
        return ClientRead.model_validate(client)

    async def delete_client(self, client_id: str) -> None:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)
            await uow.clients.delete(client)
            await uow.commit()
        await self._search.delete_document(settings.elasticsearch_clients_index, client_id)
        await self._cache.invalidate_prefix("dashboard:")

    async def _build_catalog_prices(
        self,
        uow: SQLAlchemyUnitOfWork,
        items: list[ClientWorkCatalogPriceUpsert],
    ) -> list[ClientWorkCatalogPrice]:
        if not items:
            return []

        catalog_items = {
            item.id: item
            for item in await uow.work_catalog.list_by_ids(
                [entry.work_catalog_item_id for entry in items]
            )
        }
        prices: list[ClientWorkCatalogPrice] = []
        for entry in items:
            catalog_item = catalog_items.get(entry.work_catalog_item_id)
            if catalog_item is None:
                raise NotFoundError("work_catalog_item", entry.work_catalog_item_id)
            prices.append(
                ClientWorkCatalogPrice(
                    work_catalog_item_id=catalog_item.id,
                    price=entry.price,
                    comment=entry.comment,
                    catalog_item=catalog_item,
                )
            )
        return prices

    @staticmethod
    def _map_catalog_prices(
        items: list[ClientWorkCatalogPrice],
    ) -> list[ClientWorkCatalogPriceRead]:
        return [
            ClientWorkCatalogPriceRead(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                work_catalog_item_id=item.work_catalog_item_id,
                work_catalog_item_code=item.catalog_item.code,
                work_catalog_item_name=item.catalog_item.name,
                work_catalog_item_category=item.catalog_item.category,
                price=item.price,
                comment=item.comment,
            )
            for item in items
            if item.catalog_item is not None
        ]
