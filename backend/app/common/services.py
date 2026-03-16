from __future__ import annotations

import json
from uuid import uuid4
from typing import Any

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from app.core.config import settings


class CacheService:
    def __init__(self, client: Redis):
        self._client = client

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        value = await self._client.get(key)
        if not value:
            return None
        return json.loads(value)

    async def set_json(self, key: str, payload: dict[str, Any] | list[Any], ttl_seconds: int = 300) -> None:
        await self._client.set(key, json.dumps(payload, default=str), ex=ttl_seconds)

    async def invalidate_prefix(self, prefix: str) -> None:
        async for key in self._client.scan_iter(match=f"{prefix}*"):
            await self._client.delete(key)

    async def ping(self) -> bool:
        return bool(await self._client.ping())

    async def acquire_lock(self, key: str, *, ttl_seconds: int) -> str | None:
        token = str(uuid4())
        acquired = await self._client.set(key, token, ex=ttl_seconds, nx=True)
        return token if acquired else None

    async def release_lock(self, key: str, token: str) -> None:
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        end
        return 0
        """
        await self._client.eval(script, 1, key, token)


class SearchService:
    def __init__(self, client: AsyncElasticsearch):
        self._client = client

    async def ensure_indices(self) -> None:
        await self._ensure_index(settings.elasticsearch_clients_index, self.clients_index_mappings())
        await self._ensure_index(settings.elasticsearch_executors_index, self.executors_index_mappings())
        await self._ensure_index(settings.elasticsearch_materials_index, self.materials_index_mappings())
        await self._ensure_index(settings.elasticsearch_works_index, self.works_index_mappings())

    async def _ensure_index(self, index_name: str, mappings: dict[str, Any]) -> None:
        exists = await self._client.indices.exists(index=index_name)
        if not exists:
            await self._client.indices.create(index=index_name, mappings=mappings)
            return
        await self._client.indices.put_mapping(index=index_name, properties=mappings["properties"])

    async def index_document(self, index: str, document_id: str, payload: dict[str, Any]) -> None:
        await self._client.index(index=index, id=document_id, document=payload, refresh=True)

    async def delete_document(self, index: str, document_id: str) -> None:
        await self._client.delete(index=index, id=document_id, ignore=[404], refresh=True)

    async def prepare_index(self, index: str, mappings: dict[str, Any], *, purge: bool = False) -> None:
        await self._ensure_index(index, mappings)
        if purge:
            await self._client.delete_by_query(
                index=index,
                query={"match_all": {}},
                refresh=True,
                conflicts="proceed",
                ignore_unavailable=True,
            )

    async def bulk_index_documents(
        self,
        index: str,
        documents: list[tuple[str, dict[str, Any]]],
        *,
        refresh: bool = False,
    ) -> None:
        if not documents:
            return

        operations: list[dict[str, Any]] = []
        for document_id, payload in documents:
            operations.append({"index": {"_index": index, "_id": document_id}})
            operations.append(payload)

        await self._client.bulk(operations=operations, refresh=refresh)

    async def refresh_index(self, index: str) -> None:
        await self._client.indices.refresh(index=index)

    async def search_clients(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_clients_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["name^4", "contact_person^3", "email^2", "phone^2", "address", "comment", "search_blob"],
                }
            },
            size=20,
        )
        return [hit["_id"] for hit in response["hits"]["hits"]]

    async def search_executors(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_executors_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "full_name^4",
                        "phone^2",
                        "email^2",
                        "specialization^3",
                        "hourly_rate",
                        "comment",
                        "is_active",
                        "search_blob",
                    ],
                }
            },
            size=20,
        )
        return [hit["_id"] for hit in response["hits"]["hits"]]

    async def search_materials(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_materials_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^4",
                        "category^3",
                        "unit",
                        "stock",
                        "purchase_price",
                        "average_price",
                        "supplier^2",
                        "min_stock",
                        "comment",
                        "search_blob",
                    ],
                }
            },
            size=20,
        )
        return [hit["_id"] for hit in response["hits"]["hits"]]

    async def search_works(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_works_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "order_number^5",
                        "client_name^3",
                        "client_id",
                        "executor_name^3",
                        "executor_id",
                        "work_type^4",
                        "description",
                        "status^2",
                        "received_at",
                        "deadline_at",
                        "completed_at",
                        "comment",
                        "price_for_client",
                        "cost_price",
                        "margin",
                        "additional_expenses",
                        "labor_hours",
                        "amount_paid",
                        "material_names^2",
                        "search_blob",
                    ],
                }
            },
            size=20,
        )
        return [hit["_id"] for hit in response["hits"]["hits"]]

    async def ping(self) -> bool:
        return bool(await self._client.ping())

    @staticmethod
    def clients_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "name": {"type": "text"},
                "contact_person": {"type": "text"},
                "email": {"type": "keyword"},
                "phone": {"type": "keyword"},
                "address": {"type": "text"},
                "comment": {"type": "text"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def executors_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "full_name": {"type": "text"},
                "phone": {"type": "keyword"},
                "email": {"type": "keyword"},
                "specialization": {"type": "text"},
                "hourly_rate": {"type": "keyword"},
                "comment": {"type": "text"},
                "is_active": {"type": "keyword"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def materials_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "name": {"type": "text"},
                "category": {"type": "text"},
                "unit": {"type": "keyword"},
                "stock": {"type": "keyword"},
                "purchase_price": {"type": "keyword"},
                "average_price": {"type": "keyword"},
                "supplier": {"type": "text"},
                "min_stock": {"type": "keyword"},
                "comment": {"type": "text"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def works_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "order_number": {"type": "keyword"},
                "client_name": {"type": "text"},
                "client_id": {"type": "keyword"},
                "executor_name": {"type": "text"},
                "executor_id": {"type": "keyword"},
                "work_type": {"type": "text"},
                "description": {"type": "text"},
                "status": {"type": "keyword"},
                "received_at": {"type": "keyword"},
                "deadline_at": {"type": "keyword"},
                "completed_at": {"type": "keyword"},
                "comment": {"type": "text"},
                "price_for_client": {"type": "keyword"},
                "cost_price": {"type": "keyword"},
                "margin": {"type": "keyword"},
                "additional_expenses": {"type": "keyword"},
                "labor_hours": {"type": "keyword"},
                "amount_paid": {"type": "keyword"},
                "material_names": {"type": "text"},
                "search_blob": {"type": "text"},
            }
        }
