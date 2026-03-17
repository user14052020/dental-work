from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class OrganizationProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_profiles"

    display_name: Mapped[str] = mapped_column(String(255), default="Зуботехническая лаборатория")
    legal_name: Mapped[str] = mapped_column(String(255), default="Зуботехническая лаборатория")
    short_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    legal_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mailing_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    inn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    kpp: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ogrn: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bik: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    settlement_account: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    correspondent_account: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    director_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    accountant_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vat_mode: Mapped[str] = mapped_column(String(32), default="without_vat")
    vat_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
