from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MaterialReceipt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "material_receipts"

    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items = relationship(
        "MaterialReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="MaterialReceiptItem.sort_order.asc()",
    )


class MaterialReceiptItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "material_receipt_items"
    __table_args__ = (
        UniqueConstraint("receipt_id", "sort_order", name="uq_material_receipt_items_receipt_sort_order"),
    )

    receipt_id: Mapped[str] = mapped_column(ForeignKey("material_receipts.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[str] = mapped_column(ForeignKey("materials.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    sort_order: Mapped[int] = mapped_column(default=0, index=True)

    receipt = relationship("MaterialReceipt", back_populates="items")
    material = relationship("Material", back_populates="receipt_items")


class StockMovement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "stock_movements"

    material_id: Mapped[str] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"), index=True)
    movement_type: Mapped[str] = mapped_column(String(32), index=True)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    receipt_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("material_receipts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("works.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    inventory_adjustment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("inventory_adjustments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    material = relationship("Material", back_populates="stock_movements")
    receipt = relationship("MaterialReceipt")
    work = relationship("Work")
    inventory_adjustment = relationship("InventoryAdjustment", back_populates="stock_movements")
