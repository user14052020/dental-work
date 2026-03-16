from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import MaterialUnit
from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Material(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "materials"

    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    unit: Mapped[str] = mapped_column(String(32), default=MaterialUnit.GRAM.value)
    stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    average_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    min_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    work_materials = relationship("WorkMaterial", back_populates="material")
