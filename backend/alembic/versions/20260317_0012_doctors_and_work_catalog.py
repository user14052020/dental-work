"""add doctors and work catalog

Revision ID: 20260317_0012
Revises: 20260317_0011
Create Date: 2026-03-17 23:59:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260317_0012"
down_revision = "20260317_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("client_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("specialization", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_doctors")),
    )
    op.create_index(op.f("ix_doctors_client_id"), "doctors", ["client_id"], unique=False)
    op.create_index(op.f("ix_doctors_email"), "doctors", ["email"], unique=False)
    op.create_index(op.f("ix_doctors_full_name"), "doctors", ["full_name"], unique=False)
    op.create_index(op.f("ix_doctors_is_active"), "doctors", ["is_active"], unique=False)
    op.create_index(op.f("ix_doctors_phone"), "doctors", ["phone"], unique=False)
    op.create_index(op.f("ix_doctors_specialization"), "doctors", ["specialization"], unique=False)

    op.create_table(
        "work_catalog_items",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("default_duration_hours", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_catalog_items")),
        sa.UniqueConstraint("code", name=op.f("uq_work_catalog_items_code")),
    )
    op.create_index(op.f("ix_work_catalog_items_category"), "work_catalog_items", ["category"], unique=False)
    op.create_index(op.f("ix_work_catalog_items_code"), "work_catalog_items", ["code"], unique=True)
    op.create_index(op.f("ix_work_catalog_items_is_active"), "work_catalog_items", ["is_active"], unique=False)
    op.create_index(op.f("ix_work_catalog_items_name"), "work_catalog_items", ["name"], unique=False)

    op.create_table(
        "work_catalog_item_operations",
        sa.Column("catalog_item_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("operation_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="1.00"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["catalog_item_id"], ["work_catalog_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_id"], ["operation_catalog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_catalog_item_operations")),
        sa.UniqueConstraint(
            "catalog_item_id",
            "operation_id",
            "sort_order",
            name="uq_work_catalog_item_operations_line",
        ),
    )
    op.create_index(
        op.f("ix_work_catalog_item_operations_catalog_item_id"),
        "work_catalog_item_operations",
        ["catalog_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_work_catalog_item_operations_operation_id"),
        "work_catalog_item_operations",
        ["operation_id"],
        unique=False,
    )

    op.add_column("works", sa.Column("doctor_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("works", sa.Column("work_catalog_item_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_index(op.f("ix_works_doctor_id"), "works", ["doctor_id"], unique=False)
    op.create_index(op.f("ix_works_work_catalog_item_id"), "works", ["work_catalog_item_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_works_doctor_id_doctors"),
        "works",
        "doctors",
        ["doctor_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_works_work_catalog_item_id_work_catalog_items"),
        "works",
        "work_catalog_items",
        ["work_catalog_item_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.alter_column("doctors", "is_active", server_default=None)
    op.alter_column("work_catalog_items", "base_price", server_default=None)
    op.alter_column("work_catalog_items", "default_duration_hours", server_default=None)
    op.alter_column("work_catalog_items", "is_active", server_default=None)
    op.alter_column("work_catalog_items", "sort_order", server_default=None)
    op.alter_column("work_catalog_item_operations", "quantity", server_default=None)
    op.alter_column("work_catalog_item_operations", "sort_order", server_default=None)


def downgrade() -> None:
    op.drop_constraint(op.f("fk_works_work_catalog_item_id_work_catalog_items"), "works", type_="foreignkey")
    op.drop_constraint(op.f("fk_works_doctor_id_doctors"), "works", type_="foreignkey")
    op.drop_index(op.f("ix_works_work_catalog_item_id"), table_name="works")
    op.drop_index(op.f("ix_works_doctor_id"), table_name="works")
    op.drop_column("works", "work_catalog_item_id")
    op.drop_column("works", "doctor_id")

    op.drop_index(op.f("ix_work_catalog_item_operations_operation_id"), table_name="work_catalog_item_operations")
    op.drop_index(op.f("ix_work_catalog_item_operations_catalog_item_id"), table_name="work_catalog_item_operations")
    op.drop_table("work_catalog_item_operations")

    op.drop_index(op.f("ix_work_catalog_items_name"), table_name="work_catalog_items")
    op.drop_index(op.f("ix_work_catalog_items_is_active"), table_name="work_catalog_items")
    op.drop_index(op.f("ix_work_catalog_items_code"), table_name="work_catalog_items")
    op.drop_index(op.f("ix_work_catalog_items_category"), table_name="work_catalog_items")
    op.drop_table("work_catalog_items")

    op.drop_index(op.f("ix_doctors_specialization"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_phone"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_is_active"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_full_name"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_email"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_client_id"), table_name="doctors")
    op.drop_table("doctors")
