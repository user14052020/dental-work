from __future__ import annotations

from app.common.payroll_periods import (
    DEFAULT_PAYROLL_PERIOD_START_DAYS,
    build_payroll_periods_preview,
    normalize_payroll_period_start_days,
)
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
    "payroll_period_start_days": DEFAULT_PAYROLL_PERIOD_START_DAYS.copy(),
    "smtp_port": 587,
    "smtp_use_tls": True,
    "smtp_use_ssl": False,
}


class OrganizationService:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    @staticmethod
    def _build_profile_read(profile: OrganizationProfile) -> OrganizationProfileRead:
        payroll_period_start_days = normalize_payroll_period_start_days(getattr(profile, "payroll_period_start_days", None))
        base_payload = OrganizationProfileRead.model_validate(profile).model_dump()
        return OrganizationProfileRead.model_validate(
            {
                **base_payload,
                **build_vat_snapshot(profile.vat_mode, profile.vat_label),
                "payroll_period_start_days": payroll_period_start_days,
                "payroll_periods_preview": build_payroll_periods_preview(payroll_period_start_days),
                "smtp_password_configured": bool(getattr(profile, "smtp_password", None)),
                "smtp_enabled": bool(getattr(profile, "smtp_host", None) and getattr(profile, "smtp_from_email", None)),
            }
        )

    async def get_profile(self) -> OrganizationProfileRead:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            if profile is None:
                profile = await uow.organization.add_profile(OrganizationProfile(**DEFAULT_PROFILE_VALUES))
                await uow.commit()
            vat_mode = resolve_vat_mode(getattr(profile, "vat_mode", None), getattr(profile, "vat_label", None))
            vat_label = get_vat_label(vat_mode)
            payroll_period_start_days = normalize_payroll_period_start_days(
                getattr(profile, "payroll_period_start_days", None)
            )
            if (
                getattr(profile, "vat_mode", None) != vat_mode
                or getattr(profile, "vat_label", None) != vat_label
                or getattr(profile, "payroll_period_start_days", None) != payroll_period_start_days
            ):
                profile.vat_mode = vat_mode
                profile.vat_label = vat_label
                profile.payroll_period_start_days = payroll_period_start_days
                await uow.commit()
            return self._build_profile_read(profile)

    async def upsert_profile(self, payload: OrganizationProfileUpsert) -> OrganizationProfileRead:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            payload_data = payload.model_dump(exclude={"smtp_password", "clear_smtp_password"})
            payload_data["vat_label"] = get_vat_label(payload_data["vat_mode"])
            payload_data["payroll_period_start_days"] = normalize_payroll_period_start_days(
                payload_data.get("payroll_period_start_days")
            )
            smtp_password = payload.smtp_password.strip() if payload.smtp_password else None
            if profile is None:
                if smtp_password is not None:
                    payload_data["smtp_password"] = smtp_password
                profile = await uow.organization.add_profile(OrganizationProfile(**payload_data))
            else:
                for field, value in payload_data.items():
                    setattr(profile, field, value)
                if payload.clear_smtp_password:
                    profile.smtp_password = None
                elif smtp_password is not None:
                    profile.smtp_password = smtp_password
            await uow.commit()
            return self._build_profile_read(profile)

    async def get_profile_or_raise(self) -> OrganizationProfile:
        async with self._uow as uow:
            profile = await uow.organization.get_profile()
            if profile is None:
                raise NotFoundError("organization_profile", "default")
            return profile
