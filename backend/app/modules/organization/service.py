from __future__ import annotations

from app.common.vat import DEFAULT_VAT_MODE, build_vat_snapshot, get_vat_label, resolve_vat_mode
from app.core.exceptions import NotFoundError
from app.db.models.organization import OrganizationProfile
from app.db.unitofwork import SQLAlchemyUnitOfWork
from app.modules.organization.schemas import OrganizationProfileRead, OrganizationProfileUpsert


DEFAULT_PROFILE_VALUES = {
    "display_name": "Зуботехническая лаборатория",
    "legal_name": "Зуботехническая лаборатория",
    "vat_mode": DEFAULT_VAT_MODE,
    "vat_label": get_vat_label(DEFAULT_VAT_MODE),
}


class OrganizationService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    async def get_profile(self) -> OrganizationProfileRead:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            if profile is None:
                profile = await uow.organization.add_profile(OrganizationProfile(**DEFAULT_PROFILE_VALUES))
                await uow.commit()
            vat_mode = resolve_vat_mode(getattr(profile, "vat_mode", None), getattr(profile, "vat_label", None))
            vat_label = get_vat_label(vat_mode)
            if getattr(profile, "vat_mode", None) != vat_mode or getattr(profile, "vat_label", None) != vat_label:
                profile.vat_mode = vat_mode
                profile.vat_label = vat_label
                await uow.commit()
            return OrganizationProfileRead.model_validate(profile).model_copy(
                update=build_vat_snapshot(profile.vat_mode, profile.vat_label)
            )

    async def upsert_profile(self, payload: OrganizationProfileUpsert) -> OrganizationProfileRead:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            payload_data = payload.model_dump()
            payload_data["vat_label"] = get_vat_label(payload_data["vat_mode"])
            if profile is None:
                profile = await uow.organization.add_profile(OrganizationProfile(**payload_data))
            else:
                for field, value in payload_data.items():
                    setattr(profile, field, value)
            await uow.commit()
            return OrganizationProfileRead.model_validate(profile).model_copy(
                update=build_vat_snapshot(profile.vat_mode, profile.vat_label)
            )

    async def get_profile_or_raise(self) -> OrganizationProfile:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            if profile is None:
                raise NotFoundError("organization_profile", "default")
            return profile
