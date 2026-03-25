from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Executor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "executors"

    full_name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_category_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("executor_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    works = relationship("Work", back_populates="executor")
    payment_category = relationship("ExecutorCategory", back_populates="executors")
    work_operations = relationship("WorkOperation", back_populates="executor")
    user = relationship("User", back_populates="executor", uselist=False)
