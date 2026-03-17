from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ClientWorkCatalogPrice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "client_work_catalog_prices"
    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "work_catalog_item_id",
            name="uq_client_work_catalog_prices_client_item",
        ),
    )

    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    work_catalog_item_id: Mapped[str] = mapped_column(
        ForeignKey("work_catalog_items.id", ondelete="CASCADE"),
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client = relationship("Client", back_populates="catalog_prices")
    catalog_item = relationship("WorkCatalogItem", back_populates="client_prices")
