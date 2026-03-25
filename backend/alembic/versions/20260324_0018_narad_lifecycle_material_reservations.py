"""narad lifecycle material reservations

Revision ID: 20260324_0018
Revises: 20260324_0017
Create Date: 2026-03-24 22:15:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260324_0018"
down_revision = "20260324_0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "materials",
        sa.Column("reserved_stock", sa.Numeric(precision=12, scale=3), nullable=False, server_default="0.000"),
    )
    op.add_column("work_materials", sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("work_materials", sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        """
        UPDATE work_materials
        SET consumed_at = COALESCE(updated_at, created_at, NOW())
        """
    )
    op.alter_column("materials", "reserved_stock", server_default=None)


def downgrade() -> None:
    op.drop_column("work_materials", "consumed_at")
    op.drop_column("work_materials", "reserved_at")
    op.drop_column("materials", "reserved_stock")
