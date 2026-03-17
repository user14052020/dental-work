from __future__ import annotations

from types import SimpleNamespace

import pytest
from elasticsearch import BadRequestError

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
    def __init__(self, *, exists: bool, raise_on_create: Exception | None = None):
        self._exists = exists
        self._raise_on_create = raise_on_create
        self.create_calls: list[tuple[str, dict]] = []
        self.put_mapping_calls: list[tuple[str, dict]] = []

    async def exists(self, *, index: str):
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
