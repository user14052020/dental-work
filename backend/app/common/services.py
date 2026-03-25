from __future__ import annotations

import asyncio
import json
from uuid import uuid4
from typing import Any

from elasticsearch import AsyncElasticsearch, BadRequestError
from elastic_transport import ConnectionError as ElasticTransportConnectionError, ConnectionTimeout
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
        for attempt in range(5):
            try:
                await self._ensure_index(settings.elasticsearch_clients_index, self.clients_index_mappings())
                await self._ensure_index(settings.elasticsearch_doctors_index, self.doctors_index_mappings())
                await self._ensure_index(settings.elasticsearch_executors_index, self.executors_index_mappings())
                await self._ensure_index(settings.elasticsearch_materials_index, self.materials_index_mappings())
                await self._ensure_index(settings.elasticsearch_operations_index, self.operations_index_mappings())
                await self._ensure_index(settings.elasticsearch_work_catalog_index, self.work_catalog_index_mappings())
                await self._ensure_index(settings.elasticsearch_works_index, self.works_index_mappings())
                return
            except (ConnectionTimeout, ElasticTransportConnectionError):
                if attempt == 4:
                    raise
                await asyncio.sleep(1 + attempt)

    async def _ensure_index(self, index_name: str, mappings: dict[str, Any]) -> None:
        exists = await self._client.indices.exists(index=index_name)
        if not exists:
            try:
                await self._client.indices.create(index=index_name, mappings=mappings)
            except BadRequestError as exc:
                if not self._is_index_already_exists_error(exc):
                    raise
                await self._client.indices.put_mapping(index=index_name, properties=mappings["properties"])
            return
        await self._client.indices.put_mapping(index=index_name, properties=mappings["properties"])

    @staticmethod
    def _is_index_already_exists_error(exc: BadRequestError) -> bool:
        if getattr(exc, "error", None) == "resource_already_exists_exception":
            return True

        body = getattr(exc, "body", None)
        if isinstance(body, dict):
            error = body.get("error")
            if isinstance(error, dict) and error.get("type") == "resource_already_exists_exception":
                return True

        return False

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
                    "fields": [
                        "name^4",
                        "contact_person^3",
                        "email^2",
                        "phone^2",
                        "address",
                        "delivery_address^2",
                        "delivery_contact^2",
                        "delivery_phone^2",
                        "legal_name^4",
                        "legal_address^2",
                        "inn^4",
                        "kpp^3",
                        "ogrn^2",
                        "bank_name^2",
                        "bik^2",
                        "settlement_account^2",
                        "correspondent_account^2",
                        "contract_number^2",
                        "contract_date",
                        "signer_name^2",
                        "default_price_adjustment_percent",
                        "catalog_price_codes^3",
                        "catalog_price_names^4",
                        "catalog_price_values^2",
                        "catalog_price_comments",
                        "comment",
                        "search_blob",
                    ],
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
                        "payment_category_name^2",
                        "payment_category_code^2",
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

    async def search_doctors(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_doctors_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "full_name^5",
                        "client_name^3",
                        "client_id",
                        "phone^2",
                        "email^2",
                        "specialization^2",
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

    async def search_operations(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_operations_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "code^4",
                        "name^5",
                        "operation_group^3",
                        "description",
                        "default_quantity",
                        "default_duration_hours",
                        "is_active",
                        "rates_summary^2",
                        "search_blob",
                    ],
                }
            },
            size=20,
        )
        return [hit["_id"] for hit in response["hits"]["hits"]]

    async def search_work_catalog(self, query: str) -> list[str]:
        response = await self._client.search(
            index=settings.elasticsearch_work_catalog_index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": [
                        "code^5",
                        "name^5",
                        "category^3",
                        "description",
                        "base_price",
                        "default_duration_hours",
                        "operation_names^2",
                        "operation_codes^2",
                        "is_active",
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
                        "client_delivery_address^2",
                        "client_delivery_contact^2",
                        "client_delivery_phone^2",
                        "client_id",
                        "executor_name^3",
                        "executor_id",
                        "doctor_id",
                        "work_type^4",
                        "work_catalog_item_id",
                        "work_catalog_item_code^4",
                        "work_catalog_item_name^4",
                        "work_catalog_item_category^2",
                        "description",
                        "doctor_name^3",
                        "doctor_phone^2",
                        "patient_name^3",
                        "patient_age",
                        "patient_gender",
                        "require_color_photo",
                        "face_shape^2",
                        "implant_system^2",
                        "metal_type^2",
                        "shade_color^2",
                        "tooth_formula^2",
                        "outside_lab_name^3",
                        "outside_order_number^2",
                        "outside_comment^2",
                        "tooth_selection_summary^2",
                        "status^2",
                        "received_at",
                        "deadline_at",
                        "completed_at",
                        "closed_at",
                        "delivery_sent",
                        "delivery_sent_at",
                        "base_price_for_client",
                        "price_adjustment_percent",
                        "price_for_client",
                        "cost_price",
                        "margin",
                        "additional_expenses",
                        "labor_hours",
                        "labor_cost",
                        "amount_paid",
                        "work_item_types^3",
                        "work_item_codes^4",
                        "work_item_descriptions^2",
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
                "delivery_address": {"type": "text"},
                "delivery_contact": {"type": "text"},
                "delivery_phone": {"type": "keyword"},
                "legal_name": {"type": "text"},
                "legal_address": {"type": "text"},
                "inn": {"type": "keyword"},
                "kpp": {"type": "keyword"},
                "ogrn": {"type": "keyword"},
                "bank_name": {"type": "text"},
                "bik": {"type": "keyword"},
                "settlement_account": {"type": "keyword"},
                "correspondent_account": {"type": "keyword"},
                "contract_number": {"type": "keyword"},
                "contract_date": {"type": "keyword"},
                "signer_name": {"type": "text"},
                "default_price_adjustment_percent": {"type": "keyword"},
                "catalog_price_codes": {"type": "keyword"},
                "catalog_price_names": {"type": "text"},
                "catalog_price_values": {"type": "keyword"},
                "catalog_price_comments": {"type": "text"},
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
                "payment_category_name": {"type": "text"},
                "payment_category_code": {"type": "keyword"},
                "hourly_rate": {"type": "keyword"},
                "comment": {"type": "text"},
                "is_active": {"type": "keyword"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def doctors_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "full_name": {"type": "text"},
                "client_name": {"type": "text"},
                "client_id": {"type": "keyword"},
                "phone": {"type": "keyword"},
                "email": {"type": "keyword"},
                "specialization": {"type": "text"},
                "comment": {"type": "text"},
                "is_active": {"type": "keyword"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def operations_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "code": {"type": "keyword"},
                "name": {"type": "text"},
                "operation_group": {"type": "text"},
                "description": {"type": "text"},
                "default_quantity": {"type": "keyword"},
                "default_duration_hours": {"type": "keyword"},
                "is_active": {"type": "keyword"},
                "rates_summary": {"type": "text"},
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
    def work_catalog_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "code": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "text"},
                "description": {"type": "text"},
                "base_price": {"type": "keyword"},
                "default_duration_hours": {"type": "keyword"},
                "operation_names": {"type": "text"},
                "operation_codes": {"type": "keyword"},
                "is_active": {"type": "keyword"},
                "search_blob": {"type": "text"},
            }
        }

    @staticmethod
    def works_index_mappings() -> dict[str, Any]:
        return {
            "properties": {
                "order_number": {"type": "keyword"},
                "client_name": {"type": "text"},
                "client_delivery_address": {"type": "text"},
                "client_delivery_contact": {"type": "text"},
                "client_delivery_phone": {"type": "keyword"},
                "client_id": {"type": "keyword"},
                "executor_name": {"type": "text"},
                "executor_id": {"type": "keyword"},
                "doctor_id": {"type": "keyword"},
                "work_catalog_item_id": {"type": "keyword"},
                "work_catalog_item_code": {"type": "keyword"},
                "work_catalog_item_name": {"type": "text"},
                "work_catalog_item_category": {"type": "text"},
                "work_type": {"type": "text"},
                "description": {"type": "text"},
                "doctor_name": {"type": "text"},
                "doctor_phone": {"type": "keyword"},
                "patient_name": {"type": "text"},
                "patient_age": {"type": "keyword"},
                "patient_gender": {"type": "keyword"},
                "require_color_photo": {"type": "keyword"},
                "face_shape": {"type": "keyword"},
                "implant_system": {"type": "text"},
                "metal_type": {"type": "text"},
                "shade_color": {"type": "text"},
                "tooth_formula": {"type": "text"},
                "is_outside_work": {"type": "keyword"},
                "outside_lab_name": {"type": "text"},
                "outside_order_number": {"type": "keyword"},
                "outside_cost": {"type": "keyword"},
                "outside_sent_at": {"type": "keyword"},
                "outside_due_at": {"type": "keyword"},
                "outside_returned_at": {"type": "keyword"},
                "outside_comment": {"type": "text"},
                "tooth_selection_summary": {"type": "text"},
                "work_item_types": {"type": "text"},
                "work_item_codes": {"type": "keyword"},
                "work_item_descriptions": {"type": "text"},
                "status": {"type": "keyword"},
                "received_at": {"type": "keyword"},
                "deadline_at": {"type": "keyword"},
                "completed_at": {"type": "keyword"},
                "closed_at": {"type": "keyword"},
                "delivery_sent": {"type": "keyword"},
                "delivery_sent_at": {"type": "keyword"},
                "base_price_for_client": {"type": "keyword"},
                "price_adjustment_percent": {"type": "keyword"},
                "price_for_client": {"type": "keyword"},
                "cost_price": {"type": "keyword"},
                "margin": {"type": "keyword"},
                "additional_expenses": {"type": "keyword"},
                "labor_hours": {"type": "keyword"},
                "labor_cost": {"type": "keyword"},
                "amount_paid": {"type": "keyword"},
                "operation_names": {"type": "text"},
                "material_names": {"type": "text"},
                "search_blob": {"type": "text"},
            }
        }
