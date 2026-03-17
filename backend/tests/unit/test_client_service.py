from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.db.models.work_catalog import WorkCatalogItem
from app.modules.clients.schemas import ClientCreate
from app.modules.clients.service import ClientService


class FakeClient:
    def __init__(self, **kwargs):
        self.id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.legal_name = None
        self.legal_address = None
        self.delivery_address = None
        self.delivery_contact = None
        self.delivery_phone = None
        self.inn = None
        self.kpp = None
        self.ogrn = None
        self.bank_name = None
        self.bik = None
        self.settlement_account = None
        self.correspondent_account = None
        self.contract_number = None
        self.contract_date = None
        self.signer_name = None
        self.catalog_prices = []
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
            delivery_address=getattr(client, "delivery_address", None),
            delivery_contact=getattr(client, "delivery_contact", None),
            delivery_phone=getattr(client, "delivery_phone", None),
            legal_name=getattr(client, "legal_name", None),
            legal_address=getattr(client, "legal_address", None),
            inn=getattr(client, "inn", None),
            kpp=getattr(client, "kpp", None),
            ogrn=getattr(client, "ogrn", None),
            bank_name=getattr(client, "bank_name", None),
            bik=getattr(client, "bik", None),
            settlement_account=getattr(client, "settlement_account", None),
            correspondent_account=getattr(client, "correspondent_account", None),
            contract_number=getattr(client, "contract_number", None),
            contract_date=getattr(client, "contract_date", None),
            signer_name=getattr(client, "signer_name", None),
            default_price_adjustment_percent=client.default_price_adjustment_percent,
            comment=client.comment,
            catalog_prices=list(getattr(client, "catalog_prices", [])),
        )
        self.saved = fake
        return fake


class FakeWorkCatalogRepository:
    def __init__(self):
        self.items = {
            "catalog-1": WorkCatalogItem(
                id="catalog-1",
                code="CAT-001",
                name="Циркониевая коронка",
                category="Ортопедия",
            ),
        }

    async def list_by_ids(self, item_ids):
        return [item for item_id, item in self.items.items() if item_id in item_ids]


class FakeContextUoW:
    def __init__(self):
        self.clients = FakeClientRepository()
        self.work_catalog = FakeWorkCatalogRepository()
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
            inn="6671456789",
            contract_number="D-2026-1",
            default_price_adjustment_percent="0",
            comment="VIP",
            work_catalog_prices=[
                {
                    "work_catalog_item_id": "catalog-1",
                    "price": "14500.00",
                    "comment": "Прайс по договору",
                }
            ],
        )
    )

    assert uow.committed is True
    assert result.name == "Nova Clinic"
    assert len(uow.clients.saved.catalog_prices) == 1
    assert str(uow.clients.saved.catalog_prices[0].price) == "14500.00"
    assert len(search.calls) == 1
    assert cache.invalidated == ["dashboard:"]
