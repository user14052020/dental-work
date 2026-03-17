from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import OperationExecutionStatus
from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ExecutorCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "executor_categories"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    executors = relationship("Executor", back_populates="payment_category")
    operation_rates = relationship(
        "OperationCategoryRate",
        back_populates="executor_category",
        cascade="all, delete-orphan",
    )
    work_operations = relationship("WorkOperation", back_populates="executor_category")


class OperationCatalog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "operation_catalog"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    operation_group: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    default_duration_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    payment_rates = relationship(
        "OperationCategoryRate",
        back_populates="operation",
        cascade="all, delete-orphan",
        order_by="OperationCategoryRate.created_at.asc()",
    )
    work_operations = relationship("WorkOperation", back_populates="operation")


class OperationCategoryRate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "operation_category_rates"
    __table_args__ = (
        UniqueConstraint("operation_id", "executor_category_id", name="uq_operation_category_rates_operation_id"),
    )

    operation_id: Mapped[str] = mapped_column(ForeignKey("operation_catalog.id", ondelete="CASCADE"), index=True)
    executor_category_id: Mapped[str] = mapped_column(
        ForeignKey("executor_categories.id", ondelete="CASCADE"),
        index=True,
    )
    labor_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    operation = relationship("OperationCatalog", back_populates="payment_rates")
    executor_category = relationship("ExecutorCategory", back_populates="operation_rates")


class WorkOperation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_operations"

    work_id: Mapped[str] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), index=True)
    operation_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("operation_catalog.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    executor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    executor_category_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("executor_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    operation_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    operation_name: Mapped[str] = mapped_column(String(255), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    unit_labor_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_labor_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String(32), default=OperationExecutionStatus.PLANNED.value, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    manual_rate_override: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    work = relationship("Work", back_populates="work_operations")
    operation = relationship("OperationCatalog", back_populates="work_operations")
    executor = relationship("Executor", back_populates="work_operations")
    executor_category = relationship("ExecutorCategory", back_populates="work_operations")
    logs = relationship(
        "WorkOperationLog",
        back_populates="work_operation",
        cascade="all, delete-orphan",
        order_by="WorkOperationLog.created_at.desc()",
    )


class WorkOperationLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_operation_logs"

    work_operation_id: Mapped[str] = mapped_column(
        ForeignKey("work_operations.id", ondelete="CASCADE"),
        index=True,
    )
    action: Mapped[str] = mapped_column(String(64), index=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    work_operation = relationship("WorkOperation", back_populates="logs")
