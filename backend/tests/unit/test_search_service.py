from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from elasticsearch import BadRequestError
from elastic_transport import ConnectionTimeout

from app.common.services import SearchService


class FakeAlreadyExistsError(BadRequestError):
    def __init__(self):
        Exception.__init__(self, "resource_already_exists_exception")

    @property
    def error(self):
        return "resource_already_exists_exception"

    @property
    def body(self):
        return {"error": {"type": "resource_already_exists_exception"}}


class FakeIndicesClient:
    def __init__(
        self,
        *,
        exists: bool,
        raise_on_create: Exception | None = None,
        raise_on_exists_attempts: int = 0,
    ):
        self._exists = exists
        self._raise_on_create = raise_on_create
        self._raise_on_exists_attempts = raise_on_exists_attempts
        self.exists_call_count = 0
        self.create_calls: list[tuple[str, dict]] = []
        self.put_mapping_calls: list[tuple[str, dict]] = []

    async def exists(self, *, index: str):
        self.exists_call_count += 1
        if self.exists_call_count <= self._raise_on_exists_attempts:
            raise ConnectionTimeout("timed out")
        return self._exists

    async def create(self, *, index: str, mappings: dict):
        self.create_calls.append((index, mappings))
        if self._raise_on_create:
            raise self._raise_on_create

    async def put_mapping(self, *, index: str, properties: dict):
        self.put_mapping_calls.append((index, properties))


@pytest.mark.asyncio
async def test_ensure_index_ignores_race_when_index_is_created_concurrently():
    indices = FakeIndicesClient(
        exists=False,
        raise_on_create=FakeAlreadyExistsError(),
    )
    service = SearchService(SimpleNamespace(indices=indices))

    mappings = {"properties": {"name": {"type": "text"}}}

    await service._ensure_index("clients", mappings)

    assert indices.create_calls == [("clients", mappings)]
    assert indices.put_mapping_calls == [("clients", mappings["properties"])]


@pytest.mark.asyncio
async def test_ensure_index_updates_mapping_for_existing_index():
    indices = FakeIndicesClient(exists=True)
    service = SearchService(SimpleNamespace(indices=indices))

    mappings = {"properties": {"name": {"type": "text"}}}

    await service._ensure_index("clients", mappings)

    assert indices.create_calls == []
    assert indices.put_mapping_calls == [("clients", mappings["properties"])]


@pytest.mark.asyncio
async def test_ensure_indices_retries_when_elasticsearch_is_not_ready(monkeypatch):
    indices = FakeIndicesClient(exists=True, raise_on_exists_attempts=1)
    service = SearchService(SimpleNamespace(indices=indices))

    async def fake_sleep(_: float):
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    await service.ensure_indices()

    assert indices.exists_call_count >= 8
