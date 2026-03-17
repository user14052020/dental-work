"""client work catalog prices

Revision ID: 20260317_0013
Revises: 20260317_0012
Create Date: 2026-03-17 23:10:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260317_0013"
down_revision = "20260317_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "client_work_catalog_prices",
        sa.Column("client_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("work_catalog_item_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_catalog_item_id"], ["work_catalog_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_client_work_catalog_prices")),
        sa.UniqueConstraint(
            "client_id",
            "work_catalog_item_id",
            name="uq_client_work_catalog_prices_client_item",
        ),
    )
    op.create_index(
        op.f("ix_client_work_catalog_prices_client_id"),
        "client_work_catalog_prices",
        ["client_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_client_work_catalog_prices_work_catalog_item_id"),
        "client_work_catalog_prices",
        ["work_catalog_item_id"],
        unique=False,
    )
    op.alter_column("client_work_catalog_prices", "price", server_default=None)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_client_work_catalog_prices_work_catalog_item_id"),
        table_name="client_work_catalog_prices",
    )
    op.drop_index(
        op.f("ix_client_work_catalog_prices_client_id"),
        table_name="client_work_catalog_prices",
    )
    op.drop_table("client_work_catalog_prices")
