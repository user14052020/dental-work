from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.modules.clients.schemas import ClientCreate
from app.modules.clients.service import ClientService


class FakeClient:
    def __init__(self, **kwargs):
        self.id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeClientRepository:
    def __init__(self):
        self.saved: FakeClient | None = None

    async def add(self, client):
        fake = FakeClient(
            name=client.name,
            contact_person=client.contact_person,
            phone=client.phone,
            email=client.email,
            address=client.address,
            comment=client.comment,
        )
        self.saved = fake
        return fake


class FakeContextUoW:
    def __init__(self):
        self.clients = FakeClientRepository()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


class FakeSearchService:
    def __init__(self):
        self.calls = []

    async def index_document(self, index, document_id, payload):
        self.calls.append((index, document_id, payload))

    async def delete_document(self, index, document_id):
        self.calls.append((index, document_id))


class FakeCacheService:
    def __init__(self):
        self.invalidated = []

    async def invalidate_prefix(self, prefix):
        self.invalidated.append(prefix)


@pytest.mark.asyncio
async def test_create_client_commits_and_indexes_document():
    uow = FakeContextUoW()
    search = FakeSearchService()
    cache = FakeCacheService()
    service = ClientService(uow=uow, search=search, cache=cache)

    result = await service.create_client(
        ClientCreate(
            name="Nova Clinic",
            contact_person="Elena",
            phone="+79991234567",
            email="elena@nova.example",
            address="Ekaterinburg",
            comment="VIP",
        )
    )

    assert uow.committed is True
    assert result.name == "Nova Clinic"
    assert len(search.calls) == 1
    assert cache.invalidated == ["dashboard:"]
