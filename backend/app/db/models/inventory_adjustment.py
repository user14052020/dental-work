from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryAdjustment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inventory_adjustments"

    adjustment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items = relationship(
        "InventoryAdjustmentItem",
        back_populates="adjustment",
        cascade="all, delete-orphan",
        order_by="InventoryAdjustmentItem.sort_order.asc()",
    )
    stock_movements = relationship("StockMovement", back_populates="inventory_adjustment")


class InventoryAdjustmentItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inventory_adjustment_items"
    __table_args__ = (
        UniqueConstraint("adjustment_id", "sort_order", name="uq_inventory_adjustment_items_adjustment_sort_order"),
    )

    adjustment_id: Mapped[str] = mapped_column(ForeignKey("inventory_adjustments.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[str] = mapped_column(ForeignKey("materials.id", ondelete="RESTRICT"), index=True)
    expected_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    actual_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    sort_order: Mapped[int] = mapped_column(default=0, index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    adjustment = relationship("InventoryAdjustment", back_populates="items")
    material = relationship("Material", back_populates="inventory_adjustment_items")
