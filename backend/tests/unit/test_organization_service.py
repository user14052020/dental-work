from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.db.models.organization import OrganizationProfile
from app.modules.organization.schemas import OrganizationProfileUpsert
from app.modules.organization.service import OrganizationService


class FakeOrganizationRepository:
    def __init__(self, profile: OrganizationProfile | None = None):
        self.profile = profile

    async def get_profile(self):
        return self.profile

    async def add_profile(self, profile: OrganizationProfile):
        if getattr(profile, "id", None) is None:
            profile.id = str(uuid4())
        if getattr(profile, "created_at", None) is None:
            profile.created_at = datetime.now(timezone.utc)
        if getattr(profile, "updated_at", None) is None:
            profile.updated_at = datetime.now(timezone.utc)
        self.profile = profile
        return profile


class FakeContextUoW:
    def __init__(self, profile: OrganizationProfile | None = None):
        self.organization = FakeOrganizationRepository(profile)
        self.committed = False
        if profile is not None:
            if getattr(profile, "id", None) is None:
                profile.id = str(uuid4())
            if getattr(profile, "created_at", None) is None:
                profile.created_at = datetime.now(timezone.utc)
            if getattr(profile, "updated_at", None) is None:
                profile.updated_at = datetime.now(timezone.utc)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_get_profile_creates_default_profile_when_missing():
    uow = FakeContextUoW()
    service = OrganizationService(uow)

    result = await service.get_profile()

    assert uow.committed is True
    assert result.display_name == "Зуботехническая лаборатория"
    assert result.legal_name == "Зуботехническая лаборатория"
    assert result.vat_mode == "without_vat"
    assert result.vat_label == "Без налога (НДС)"


@pytest.mark.asyncio
async def test_upsert_profile_updates_existing_organization_requisites():
    profile = OrganizationProfile(
        display_name="Старая лаборатория",
        legal_name="ООО Старая лаборатория",
    )
    uow = FakeContextUoW(profile)
    service = OrganizationService(uow)

    result = await service.upsert_profile(
        OrganizationProfileUpsert(
            display_name="Dental Lab Pro",
            legal_name="ООО Дентал Лаб Про",
            inn="6677001122",
            kpp="667701001",
            legal_address="Екатеринбург, ул. Мира, 1",
            bank_name="Сбербанк",
            settlement_account="40702810900000000001",
            correspondent_account="30101810400000000555",
            bik="044525555",
            recipient_name="ООО Дентал Лаб Про",
            director_name="Иванов И.И.",
            vat_mode="vat_20",
        )
    )

    assert uow.committed is True
    assert result.display_name == "Dental Lab Pro"
    assert result.legal_name == "ООО Дентал Лаб Про"
    assert result.inn == "6677001122"
    assert result.kpp == "667701001"
    assert result.bank_name == "Сбербанк"
    assert result.director_name == "Иванов И.И."
    assert result.vat_mode == "vat_20"
    assert result.vat_label == "НДС 20%"
