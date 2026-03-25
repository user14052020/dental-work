from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import PaymentMethod
from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    payment_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    method: Mapped[str] = mapped_column(String(32), default=PaymentMethod.BANK_TRANSFER.value, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    external_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client = relationship("Client", back_populates="payments")
    allocations = relationship(
        "PaymentAllocation",
        back_populates="payment",
        cascade="all, delete-orphan",
        order_by="PaymentAllocation.created_at.asc()",
    )


class PaymentAllocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_allocations"
    __table_args__ = (
        UniqueConstraint("payment_id", "work_id", name="uq_payment_allocations_payment_work"),
    )

    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), index=True)
    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    payment = relationship("Payment", back_populates="allocations")
    work = relationship("Work", back_populates="payment_allocations")
