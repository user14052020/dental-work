from __future__ import annotations

from decimal import Decimal

from app.common.pagination import PaginatedResponse
from app.common.search_documents import build_client_search_document
from app.common.services import CacheService, SearchService
from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.models.client import Client
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.clients.schemas import ClientCreate, ClientDetailRead, ClientListResponse, ClientRead, ClientUpdate
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
                },
            )

    async def create_client(self, payload: ClientCreate) -> ClientRead:
        async with self._uow as uow:
            client = await uow.clients.add(Client(**payload.model_dump()))
            await uow.commit()
        await self._search.index_document(settings.elasticsearch_clients_index, client.id, build_client_search_document(client))
        await self._cache.invalidate_prefix("dashboard:")
        return ClientRead.model_validate(client)

    async def update_client(self, client_id: str, payload: ClientUpdate) -> ClientRead:
        async with self._uow as uow:
            client = await uow.clients.get(client_id)
            if client is None:
                raise NotFoundError("client", client_id)
            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(client, field, value)
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
