from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WorkCatalogItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_catalog_items"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    default_duration_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    default_operations = relationship(
        "WorkCatalogItemOperation",
        back_populates="catalog_item",
        cascade="all, delete-orphan",
        order_by="WorkCatalogItemOperation.sort_order.asc()",
    )
    client_prices = relationship(
        "ClientWorkCatalogPrice",
        back_populates="catalog_item",
        cascade="all, delete-orphan",
    )
    works = relationship("Work", back_populates="catalog_item")


class WorkCatalogItemOperation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_catalog_item_operations"
    __table_args__ = (
        UniqueConstraint("catalog_item_id", "operation_id", "sort_order", name="uq_work_catalog_item_operations_line"),
    )

    catalog_item_id: Mapped[str] = mapped_column(
        ForeignKey("work_catalog_items.id", ondelete="CASCADE"),
        index=True,
    )
    operation_id: Mapped[str] = mapped_column(ForeignKey("operation_catalog.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    catalog_item = relationship("WorkCatalogItem", back_populates="default_operations")
    operation = relationship("OperationCatalog")
