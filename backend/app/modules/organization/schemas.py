from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import EmailStr, Field, StringConstraints, field_validator, model_validator

from app.common.payroll_periods import DEFAULT_PAYROLL_PERIOD_START_DAYS, normalize_payroll_period_start_days
from app.common.vat import DEFAULT_VAT_MODE, VatMode
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
OptionalShortString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=255)]
OptionalCodeString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=30)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=2000)]


class OrganizationProfileUpsert(BaseSchema):
    display_name: ShortString
    legal_name: ShortString
    short_name: OptionalShortString = None
    legal_address: OptionalShortString = None
    mailing_address: OptionalShortString = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    inn: OptionalCodeString = None
    kpp: OptionalCodeString = None
    ogrn: OptionalCodeString = None
    bank_name: OptionalShortString = None
    bik: OptionalCodeString = None
    settlement_account: OptionalCodeString = None
    correspondent_account: OptionalCodeString = None
    recipient_name: OptionalShortString = None
    director_name: OptionalShortString = None
    accountant_name: OptionalShortString = None
    vat_mode: VatMode = Field(default=DEFAULT_VAT_MODE)
    payroll_period_start_days: list[int] = Field(default_factory=lambda: DEFAULT_PAYROLL_PERIOD_START_DAYS.copy())
    smtp_host: OptionalShortString = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: OptionalShortString = None
    smtp_password: Optional[str] = Field(default=None, max_length=255)
    clear_smtp_password: bool = False
    smtp_from_email: Optional[EmailStr] = None
    smtp_from_name: OptionalShortString = None
    smtp_reply_to: Optional[EmailStr] = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    comment: CommentString = None

    @field_validator("payroll_period_start_days")
    @classmethod
    def validate_payroll_period_start_days(cls, value: list[int]) -> list[int]:
        return normalize_payroll_period_start_days(value)

    @model_validator(mode="after")
    def validate_smtp_transport(self):
        if self.smtp_use_tls and self.smtp_use_ssl:
            raise ValueError("Одновременно включать STARTTLS и SSL нельзя.")
        return self


class PayrollPeriodPreviewRead(BaseSchema):
    key: str
    label: str
    date_from: datetime
    date_to: datetime
    is_current: bool


class OrganizationProfileRead(TimestampedReadSchema):
    display_name: str
    legal_name: str
    short_name: Optional[str]
    legal_address: Optional[str]
    mailing_address: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    inn: Optional[str]
    kpp: Optional[str]
    ogrn: Optional[str]
    bank_name: Optional[str]
    bik: Optional[str]
    settlement_account: Optional[str]
    correspondent_account: Optional[str]
    recipient_name: Optional[str]
    director_name: Optional[str]
    accountant_name: Optional[str]
    vat_mode: VatMode = DEFAULT_VAT_MODE
    vat_label: str = "Без налога (НДС)"
    vat_rate_percent: Decimal = Decimal("0.00")
    payroll_period_start_days: list[int] = Field(default_factory=lambda: DEFAULT_PAYROLL_PERIOD_START_DAYS.copy())
    payroll_periods_preview: list[PayrollPeriodPreviewRead] = Field(default_factory=list)
    smtp_host: Optional[str]
    smtp_port: int = 587
    smtp_username: Optional[str]
    smtp_from_email: Optional[EmailStr]
    smtp_from_name: Optional[str]
    smtp_reply_to: Optional[EmailStr]
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_password_configured: bool = False
    smtp_enabled: bool = False
    comment: Optional[str]

    @field_validator("payroll_period_start_days")
    @classmethod
    def validate_payroll_period_start_days(cls, value: list[int]) -> list[int]:
        return normalize_payroll_period_start_days(value)
