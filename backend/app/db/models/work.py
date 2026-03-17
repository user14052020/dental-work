from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import WorkStatus
from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Work(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "works"

    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    executor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("executors.id", ondelete="SET NULL"), nullable=True)
    doctor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True)
    work_catalog_item_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("work_catalog_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_type: Mapped[str] = mapped_column(String(255), index=True)
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
    delivery_sent: Mapped[bool] = mapped_column(default=False, index=True)
    delivery_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    base_price_for_client: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    price_adjustment_percent: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0.00"))
    price_for_client: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    margin: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    additional_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    labor_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    client = relationship("Client", back_populates="works")
    executor = relationship("Executor", back_populates="works")
    doctor = relationship("Doctor", back_populates="works")
    catalog_item = relationship("WorkCatalogItem", back_populates="works")
    work_items = relationship(
        "WorkItem",
        back_populates="work",
        cascade="all, delete-orphan",
        order_by="WorkItem.sort_order.asc()",
    )
    materials = relationship("WorkMaterial", back_populates="work", cascade="all, delete-orphan")
    work_operations = relationship("WorkOperation", back_populates="work", cascade="all, delete-orphan")
    attachments = relationship(
        "WorkAttachment",
        back_populates="work",
        cascade="all, delete-orphan",
        order_by="WorkAttachment.created_at.desc()",
    )
    change_logs = relationship(
        "WorkChangeLog",
        back_populates="work",
        cascade="all, delete-orphan",
        order_by="WorkChangeLog.created_at.desc()",
    )

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None


class WorkMaterial(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_materials"

    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[str] = mapped_column(ForeignKey("materials.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0.000"))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    work = relationship("Work", back_populates="materials")
    material = relationship("Material", back_populates="work_materials")


class WorkItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_items"
    __table_args__ = (
        UniqueConstraint("work_id", "sort_order", name="uq_work_items_work_sort_order"),
    )

    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    work_catalog_item_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("work_catalog_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_type: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    sort_order: Mapped[int] = mapped_column(default=0, index=True)

    work = relationship("Work", back_populates="work_items")
    catalog_item = relationship("WorkCatalogItem")


class WorkChangeLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_change_logs"

    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    work = relationship("Work", back_populates="change_logs")


class WorkAttachment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_attachments"

    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    content_type: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(index=True)
    uploaded_by_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    work = relationship("Work", back_populates="attachments")
