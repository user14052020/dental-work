"""inventory adjustments

Revision ID: 20260325_0025
Revises: 20260325_0024
Create Date: 2026-03-25 18:10:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260325_0025"
down_revision = "20260325_0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_adjustments",
        sa.Column("adjustment_number", sa.String(length=50), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_adjustments")),
        sa.UniqueConstraint("adjustment_number", name=op.f("uq_inventory_adjustments_adjustment_number")),
    )
    op.create_index(
        op.f("ix_inventory_adjustments_adjustment_number"),
        "inventory_adjustments",
        ["adjustment_number"],
        unique=False,
    )
    op.create_index(op.f("ix_inventory_adjustments_recorded_at"), "inventory_adjustments", ["recorded_at"], unique=False)

    op.create_table(
        "inventory_adjustment_items",
        sa.Column("adjustment_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("expected_stock", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("actual_stock", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("quantity_delta", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["adjustment_id"], ["inventory_adjustments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_adjustment_items")),
        sa.UniqueConstraint(
            "adjustment_id",
            "sort_order",
            name="uq_inventory_adjustment_items_adjustment_sort_order",
        ),
    )
    op.create_index(
        op.f("ix_inventory_adjustment_items_adjustment_id"),
        "inventory_adjustment_items",
        ["adjustment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_adjustment_items_material_id"),
        "inventory_adjustment_items",
        ["material_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_adjustment_items_sort_order"),
        "inventory_adjustment_items",
        ["sort_order"],
        unique=False,
    )

    op.add_column(
        "stock_movements",
        sa.Column("inventory_adjustment_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_stock_movements_inventory_adjustment_id_inventory_adjustments"),
        "stock_movements",
        "inventory_adjustments",
        ["inventory_adjustment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_stock_movements_inventory_adjustment_id"),
        "stock_movements",
        ["inventory_adjustment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_inventory_adjustment_id"), table_name="stock_movements")
    op.drop_constraint(
        op.f("fk_stock_movements_inventory_adjustment_id_inventory_adjustments"),
        "stock_movements",
        type_="foreignkey",
    )
    op.drop_column("stock_movements", "inventory_adjustment_id")

    op.drop_index(op.f("ix_inventory_adjustment_items_sort_order"), table_name="inventory_adjustment_items")
    op.drop_index(op.f("ix_inventory_adjustment_items_material_id"), table_name="inventory_adjustment_items")
    op.drop_index(op.f("ix_inventory_adjustment_items_adjustment_id"), table_name="inventory_adjustment_items")
    op.drop_table("inventory_adjustment_items")

    op.drop_index(op.f("ix_inventory_adjustments_recorded_at"), table_name="inventory_adjustments")
    op.drop_index(op.f("ix_inventory_adjustments_adjustment_number"), table_name="inventory_adjustments")
    op.drop_table("inventory_adjustments")
