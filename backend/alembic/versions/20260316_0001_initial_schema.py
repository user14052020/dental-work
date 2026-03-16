"""initial schema

Revision ID: 20260316_0001
Revises:
Create Date: 2026-03-16 09:15:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260316_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clients")),
    )
    op.create_index(op.f("ix_clients_email"), "clients", ["email"], unique=False)
    op.create_index(op.f("ix_clients_name"), "clients", ["name"], unique=False)

    op.create_table(
        "executors",
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("specialization", sa.String(length=255), nullable=True),
        sa.Column("hourly_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_executors")),
    )
    op.create_index(op.f("ix_executors_email"), "executors", ["email"], unique=False)
    op.create_index(op.f("ix_executors_full_name"), "executors", ["full_name"], unique=False)
    op.create_index(op.f("ix_executors_is_active"), "executors", ["is_active"], unique=False)

    op.create_table(
        "materials",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("stock", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("purchase_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("average_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("supplier", sa.String(length=255), nullable=True),
        sa.Column("min_stock", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materials")),
    )
    op.create_index(op.f("ix_materials_category"), "materials", ["category"], unique=False)
    op.create_index(op.f("ix_materials_name"), "materials", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "works",
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("executor_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("work_type", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_for_client", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("margin", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("additional_expenses", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("labor_hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name=op.f("fk_works_client_id_clients"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["executor_id"], ["executors.id"], name=op.f("fk_works_executor_id_executors"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_works")),
    )
    op.create_index(op.f("ix_works_client_id"), "works", ["client_id"], unique=False)
    op.create_index(op.f("ix_works_deadline_at"), "works", ["deadline_at"], unique=False)
    op.create_index(op.f("ix_works_executor_id"), "works", ["executor_id"], unique=False)
    op.create_index(op.f("ix_works_order_number"), "works", ["order_number"], unique=True)
    op.create_index(op.f("ix_works_received_at"), "works", ["received_at"], unique=False)
    op.create_index(op.f("ix_works_status"), "works", ["status"], unique=False)
    op.create_index(op.f("ix_works_work_type"), "works", ["work_type"], unique=False)

    op.create_table(
        "work_materials",
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], name=op.f("fk_work_materials_material_id_materials"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], name=op.f("fk_work_materials_work_id_works"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_materials")),
    )
    op.create_index(op.f("ix_work_materials_material_id"), "work_materials", ["material_id"], unique=False)
    op.create_index(op.f("ix_work_materials_work_id"), "work_materials", ["work_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_materials_work_id"), table_name="work_materials")
    op.drop_index(op.f("ix_work_materials_material_id"), table_name="work_materials")
    op.drop_table("work_materials")

    op.drop_index(op.f("ix_works_work_type"), table_name="works")
    op.drop_index(op.f("ix_works_status"), table_name="works")
    op.drop_index(op.f("ix_works_received_at"), table_name="works")
    op.drop_index(op.f("ix_works_order_number"), table_name="works")
    op.drop_index(op.f("ix_works_executor_id"), table_name="works")
    op.drop_index(op.f("ix_works_deadline_at"), table_name="works")
    op.drop_index(op.f("ix_works_client_id"), table_name="works")
    op.drop_table("works")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_materials_name"), table_name="materials")
    op.drop_index(op.f("ix_materials_category"), table_name="materials")
    op.drop_table("materials")

    op.drop_index(op.f("ix_executors_is_active"), table_name="executors")
    op.drop_index(op.f("ix_executors_full_name"), table_name="executors")
    op.drop_index(op.f("ix_executors_email"), table_name="executors")
    op.drop_table("executors")

    op.drop_index(op.f("ix_clients_name"), table_name="clients")
    op.drop_index(op.f("ix_clients_email"), table_name="clients")
    op.drop_table("clients")
