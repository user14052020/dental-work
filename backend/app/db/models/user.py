from typing import Optional

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255), index=True, default="Сотрудник лаборатории")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_fired: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    permission_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    executor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    executor = relationship("Executor", back_populates="user")
