"""operations module

Revision ID: 20260317_0006
Revises: 20260316_0005
Create Date: 2026-03-17 00:20:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260317_0006"
down_revision = "20260316_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "executor_categories",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_executor_categories")),
        sa.UniqueConstraint("code", name=op.f("uq_executor_categories_code")),
    )
    op.create_index(op.f("ix_executor_categories_code"), "executor_categories", ["code"], unique=False)
    op.create_index(op.f("ix_executor_categories_is_active"), "executor_categories", ["is_active"], unique=False)
    op.create_index(op.f("ix_executor_categories_name"), "executor_categories", ["name"], unique=False)

    op.add_column("executors", sa.Column("payment_category_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_index(op.f("ix_executors_payment_category_id"), "executors", ["payment_category_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_executors_payment_category_id_executor_categories"),
        "executors",
        "executor_categories",
        ["payment_category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "operation_catalog",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("operation_group", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("default_duration_hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_operation_catalog")),
        sa.UniqueConstraint("code", name=op.f("uq_operation_catalog_code")),
    )
    op.create_index(op.f("ix_operation_catalog_code"), "operation_catalog", ["code"], unique=False)
    op.create_index(op.f("ix_operation_catalog_is_active"), "operation_catalog", ["is_active"], unique=False)
    op.create_index(op.f("ix_operation_catalog_name"), "operation_catalog", ["name"], unique=False)
    op.create_index(op.f("ix_operation_catalog_operation_group"), "operation_catalog", ["operation_group"], unique=False)

    op.create_table(
        "operation_category_rates",
        sa.Column("operation_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("executor_category_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("labor_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["executor_category_id"],
            ["executor_categories.id"],
            name=op.f("fk_operation_category_rates_executor_category_id_executor_categories"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation_catalog.id"],
            name=op.f("fk_operation_category_rates_operation_id_operation_catalog"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_operation_category_rates")),
        sa.UniqueConstraint(
            "operation_id",
            "executor_category_id",
            name="uq_operation_category_rates_operation_id",
        ),
    )
    op.create_index(op.f("ix_operation_category_rates_executor_category_id"), "operation_category_rates", ["executor_category_id"], unique=False)
    op.create_index(op.f("ix_operation_category_rates_operation_id"), "operation_category_rates", ["operation_id"], unique=False)

    op.create_table(
        "work_operations",
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("operation_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("executor_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("executor_category_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("operation_code", sa.String(length=50), nullable=True),
        sa.Column("operation_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit_labor_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_labor_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("manual_rate_override", sa.Boolean(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["executor_category_id"],
            ["executor_categories.id"],
            name=op.f("fk_work_operations_executor_category_id_executor_categories"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["executor_id"],
            ["executors.id"],
            name=op.f("fk_work_operations_executor_id_executors"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation_catalog.id"],
            name=op.f("fk_work_operations_operation_id_operation_catalog"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("fk_work_operations_work_id_works"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_operations")),
    )
    op.create_index(op.f("ix_work_operations_executor_category_id"), "work_operations", ["executor_category_id"], unique=False)
    op.create_index(op.f("ix_work_operations_executor_id"), "work_operations", ["executor_id"], unique=False)
    op.create_index(op.f("ix_work_operations_operation_code"), "work_operations", ["operation_code"], unique=False)
    op.create_index(op.f("ix_work_operations_operation_id"), "work_operations", ["operation_id"], unique=False)
    op.create_index(op.f("ix_work_operations_operation_name"), "work_operations", ["operation_name"], unique=False)
    op.create_index(op.f("ix_work_operations_status"), "work_operations", ["status"], unique=False)
    op.create_index(op.f("ix_work_operations_work_id"), "work_operations", ["work_id"], unique=False)

    op.create_table(
        "work_operation_logs",
        sa.Column("work_operation_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["work_operation_id"],
            ["work_operations.id"],
            name=op.f("fk_work_operation_logs_work_operation_id_work_operations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_operation_logs")),
    )
    op.create_index(op.f("ix_work_operation_logs_action"), "work_operation_logs", ["action"], unique=False)
    op.create_index(op.f("ix_work_operation_logs_work_operation_id"), "work_operation_logs", ["work_operation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_operation_logs_work_operation_id"), table_name="work_operation_logs")
    op.drop_index(op.f("ix_work_operation_logs_action"), table_name="work_operation_logs")
    op.drop_table("work_operation_logs")

    op.drop_index(op.f("ix_work_operations_work_id"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_status"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_operation_name"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_operation_id"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_operation_code"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_executor_id"), table_name="work_operations")
    op.drop_index(op.f("ix_work_operations_executor_category_id"), table_name="work_operations")
    op.drop_table("work_operations")

    op.drop_index(op.f("ix_operation_category_rates_operation_id"), table_name="operation_category_rates")
    op.drop_index(op.f("ix_operation_category_rates_executor_category_id"), table_name="operation_category_rates")
    op.drop_table("operation_category_rates")

    op.drop_index(op.f("ix_operation_catalog_operation_group"), table_name="operation_catalog")
    op.drop_index(op.f("ix_operation_catalog_name"), table_name="operation_catalog")
    op.drop_index(op.f("ix_operation_catalog_is_active"), table_name="operation_catalog")
    op.drop_index(op.f("ix_operation_catalog_code"), table_name="operation_catalog")
    op.drop_table("operation_catalog")

    op.drop_constraint(op.f("fk_executors_payment_category_id_executor_categories"), "executors", type_="foreignkey")
    op.drop_index(op.f("ix_executors_payment_category_id"), table_name="executors")
    op.drop_column("executors", "payment_category_id")

    op.drop_index(op.f("ix_executor_categories_name"), table_name="executor_categories")
    op.drop_index(op.f("ix_executor_categories_is_active"), table_name="executor_categories")
    op.drop_index(op.f("ix_executor_categories_code"), table_name="executor_categories")
    op.drop_table("executor_categories")
