"""warehouse receipts and stock movements

Revision ID: 20260324_0017
Revises: 20260324_0016
Create Date: 2026-03-24 20:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260324_0017"
down_revision = "20260324_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "material_receipts",
        sa.Column("receipt_number", sa.String(length=50), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("supplier", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_material_receipts")),
        sa.UniqueConstraint("receipt_number", name=op.f("uq_material_receipts_receipt_number")),
    )
    op.create_index(op.f("ix_material_receipts_receipt_number"), "material_receipts", ["receipt_number"], unique=False)
    op.create_index(op.f("ix_material_receipts_received_at"), "material_receipts", ["received_at"], unique=False)
    op.create_index(op.f("ix_material_receipts_supplier"), "material_receipts", ["supplier"], unique=False)

    op.create_table(
        "material_receipt_items",
        sa.Column("receipt_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["receipt_id"], ["material_receipts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_material_receipt_items")),
        sa.UniqueConstraint("receipt_id", "sort_order", name="uq_material_receipt_items_receipt_sort_order"),
    )
    op.create_index(op.f("ix_material_receipt_items_material_id"), "material_receipt_items", ["material_id"], unique=False)
    op.create_index(op.f("ix_material_receipt_items_receipt_id"), "material_receipt_items", ["receipt_id"], unique=False)
    op.create_index(op.f("ix_material_receipt_items_sort_order"), "material_receipt_items", ["sort_order"], unique=False)

    op.create_table(
        "stock_movements",
        sa.Column("material_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("movement_type", sa.String(length=32), nullable=False),
        sa.Column("quantity_delta", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["receipt_id"], ["material_receipts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stock_movements")),
    )
    op.create_index(op.f("ix_stock_movements_material_id"), "stock_movements", ["material_id"], unique=False)
    op.create_index(op.f("ix_stock_movements_movement_type"), "stock_movements", ["movement_type"], unique=False)
    op.create_index(op.f("ix_stock_movements_receipt_id"), "stock_movements", ["receipt_id"], unique=False)
    op.create_index(op.f("ix_stock_movements_work_id"), "stock_movements", ["work_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_work_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_receipt_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_movement_type"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_material_id"), table_name="stock_movements")
    op.drop_table("stock_movements")

    op.drop_index(op.f("ix_material_receipt_items_sort_order"), table_name="material_receipt_items")
    op.drop_index(op.f("ix_material_receipt_items_receipt_id"), table_name="material_receipt_items")
    op.drop_index(op.f("ix_material_receipt_items_material_id"), table_name="material_receipt_items")
    op.drop_table("material_receipt_items")

    op.drop_index(op.f("ix_material_receipts_supplier"), table_name="material_receipts")
    op.drop_index(op.f("ix_material_receipts_received_at"), table_name="material_receipts")
    op.drop_index(op.f("ix_material_receipts_receipt_number"), table_name="material_receipts")
    op.drop_table("material_receipts")
