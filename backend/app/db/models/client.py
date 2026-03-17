from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(String(255), index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    delivery_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    delivery_contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    delivery_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    legal_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    inn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    kpp: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ogrn: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bik: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    settlement_account: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    correspondent_account: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    contract_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contract_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    signer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    default_price_adjustment_percent: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=Decimal("0.00")
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    works = relationship("Work", back_populates="client")
    doctors = relationship("Doctor", back_populates="client")
    catalog_prices = relationship(
        "ClientWorkCatalogPrice",
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="ClientWorkCatalogPrice.created_at.asc()",
    )
