"""work items

Revision ID: 20260317_0014
Revises: 20260317_0013
Create Date: 2026-03-17 23:55:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260317_0014"
down_revision = "20260317_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_items",
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("work_catalog_item_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("work_type", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False, server_default="1.00"),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["work_catalog_item_id"], ["work_catalog_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_items")),
        sa.UniqueConstraint("work_id", "sort_order", name="uq_work_items_work_sort_order"),
    )
    op.create_index(op.f("ix_work_items_sort_order"), "work_items", ["sort_order"], unique=False)
    op.create_index(op.f("ix_work_items_work_catalog_item_id"), "work_items", ["work_catalog_item_id"], unique=False)
    op.create_index(op.f("ix_work_items_work_id"), "work_items", ["work_id"], unique=False)
    op.create_index(op.f("ix_work_items_work_type"), "work_items", ["work_type"], unique=False)
    op.execute(
        """
        INSERT INTO work_items (
            work_id,
            work_catalog_item_id,
            work_type,
            description,
            quantity,
            unit_price,
            total_price,
            sort_order,
            id,
            created_at,
            updated_at
        )
        SELECT
            works.id,
            works.work_catalog_item_id,
            works.work_type,
            works.description,
            1.00,
            works.price_for_client,
            works.price_for_client,
            0,
            works.id,
            works.created_at,
            works.updated_at
        FROM works
        """
    )
    op.alter_column("work_items", "quantity", server_default=None)
    op.alter_column("work_items", "unit_price", server_default=None)
    op.alter_column("work_items", "total_price", server_default=None)
    op.alter_column("work_items", "sort_order", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_items_work_type"), table_name="work_items")
    op.drop_index(op.f("ix_work_items_work_id"), table_name="work_items")
    op.drop_index(op.f("ix_work_items_work_catalog_item_id"), table_name="work_items")
    op.drop_index(op.f("ix_work_items_sort_order"), table_name="work_items")
    op.drop_table("work_items")
