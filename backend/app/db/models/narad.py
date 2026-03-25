from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import WorkStatus
from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Narad(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "narads"

    narad_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    doctor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("doctors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contractor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("contractors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    doctor_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    patient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    patient_age: Mapped[Optional[int]] = mapped_column(nullable=True)
    patient_gender: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, index=True)
    require_color_photo: Mapped[bool] = mapped_column(default=False)
    face_shape: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    implant_system: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metal_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    shade_color: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tooth_formula: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tooth_selection: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=WorkStatus.NEW.value, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_outside_work: Mapped[bool] = mapped_column(default=False, index=True)
    outside_lab_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    outside_order_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    outside_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    outside_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    outside_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    outside_returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    outside_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client = relationship("Client", back_populates="narads")
    doctor = relationship("Doctor", back_populates="narads")
    contractor = relationship("Contractor", back_populates="narads")
    works = relationship(
        "Work",
        back_populates="narad",
        order_by="Work.received_at.asc()",
    )
    status_logs = relationship(
        "NaradStatusLog",
        back_populates="narad",
        cascade="all, delete-orphan",
        order_by="NaradStatusLog.created_at.desc()",
    )

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None


class NaradStatusLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "narad_status_logs"

    narad_id: Mapped[str] = mapped_column(ForeignKey("narads.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str] = mapped_column(String(32), index=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    narad = relationship("Narad", back_populates="status_logs")
