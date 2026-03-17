from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import EmailStr, Field, StringConstraints

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
    comment: CommentString = None


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
    comment: Optional[str]
