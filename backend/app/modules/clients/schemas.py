from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import EmailStr, Field, StringConstraints

from app.common.pagination import PaginatedResponse
from app.common.schemas import BaseSchema, PhoneString, TimestampedReadSchema
from app.modules.payments.schemas import PaymentCompactRead
from app.modules.works.schemas import WorkCompactRead


ShortString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
CommentString = Annotated[Optional[str], StringConstraints(strip_whitespace=True, max_length=1000)]


class ClientWorkCatalogPriceUpsert(BaseSchema):
    work_catalog_item_id: str
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    comment: CommentString = None


class ClientWorkCatalogPriceRead(TimestampedReadSchema):
    work_catalog_item_id: str
    work_catalog_item_code: str
    work_catalog_item_name: str
    work_catalog_item_category: Optional[str]
    price: Decimal
    comment: Optional[str]


class ClientCreate(BaseSchema):
    name: ShortString
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=255)
    delivery_contact: Optional[str] = Field(default=None, max_length=255)
    delivery_phone: Optional[PhoneString] = None
    legal_name: Optional[str] = Field(default=None, max_length=255)
    legal_address: Optional[str] = Field(default=None, max_length=255)
    inn: Optional[str] = Field(default=None, max_length=20)
    kpp: Optional[str] = Field(default=None, max_length=20)
    ogrn: Optional[str] = Field(default=None, max_length=30)
    bank_name: Optional[str] = Field(default=None, max_length=255)
    bik: Optional[str] = Field(default=None, max_length=20)
    settlement_account: Optional[str] = Field(default=None, max_length=30)
    correspondent_account: Optional[str] = Field(default=None, max_length=30)
    contract_number: Optional[str] = Field(default=None, max_length=100)
    contract_date: Optional[date] = None
    signer_name: Optional[str] = Field(default=None, max_length=255)
    default_price_adjustment_percent: Decimal = Field(default=Decimal("0.00"), ge=-100, le=1000)
    comment: CommentString = None
    work_catalog_prices: list[ClientWorkCatalogPriceUpsert] = Field(default_factory=list)


class ClientUpdate(BaseSchema):
    name: Optional[ShortString] = None
    contact_person: Optional[ShortString] = None
    phone: Optional[PhoneString] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=255)
    delivery_address: Optional[str] = Field(default=None, max_length=255)
    delivery_contact: Optional[str] = Field(default=None, max_length=255)
    delivery_phone: Optional[PhoneString] = None
    legal_name: Optional[str] = Field(default=None, max_length=255)
    legal_address: Optional[str] = Field(default=None, max_length=255)
    inn: Optional[str] = Field(default=None, max_length=20)
    kpp: Optional[str] = Field(default=None, max_length=20)
    ogrn: Optional[str] = Field(default=None, max_length=30)
    bank_name: Optional[str] = Field(default=None, max_length=255)
    bik: Optional[str] = Field(default=None, max_length=20)
    settlement_account: Optional[str] = Field(default=None, max_length=30)
    correspondent_account: Optional[str] = Field(default=None, max_length=30)
    contract_number: Optional[str] = Field(default=None, max_length=100)
    contract_date: Optional[date] = None
    signer_name: Optional[str] = Field(default=None, max_length=255)
    default_price_adjustment_percent: Optional[Decimal] = Field(default=None, ge=-100, le=1000)
    comment: CommentString = None
    work_catalog_prices: Optional[list[ClientWorkCatalogPriceUpsert]] = None


class ClientRead(TimestampedReadSchema):
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    delivery_address: Optional[str]
    delivery_contact: Optional[str]
    delivery_phone: Optional[str]
    legal_name: Optional[str]
    legal_address: Optional[str]
    inn: Optional[str]
    kpp: Optional[str]
    ogrn: Optional[str]
    bank_name: Optional[str]
    bik: Optional[str]
    settlement_account: Optional[str]
    correspondent_account: Optional[str]
    contract_number: Optional[str]
    contract_date: Optional[date]
    signer_name: Optional[str]
    default_price_adjustment_percent: Decimal = Decimal("0.00")
    comment: Optional[str]
    work_count: int = 0
    order_total: Decimal = Decimal("0.00")
    paid_total: Decimal = Decimal("0.00")
    unpaid_total: Decimal = Decimal("0.00")


class ClientDetailRead(ClientRead):
    recent_works: list[WorkCompactRead] = []
    recent_payments: list[PaymentCompactRead] = Field(default_factory=list)
    work_catalog_prices: list[ClientWorkCatalogPriceRead] = Field(default_factory=list)


class ClientListResponse(PaginatedResponse[ClientRead]):
    pass
