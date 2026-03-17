"""work enhancements

Revision ID: 20260316_0003
Revises: 20260316_0002
Create Date: 2026-03-16 23:10:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260316_0003"
down_revision = "20260316_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("default_price_adjustment_percent", sa.Numeric(precision=6, scale=2), nullable=False, server_default="0.00"),
    )

    op.add_column("works", sa.Column("doctor_name", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("patient_name", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("tooth_formula", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "works",
        sa.Column("base_price_for_client", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "works",
        sa.Column("price_adjustment_percent", sa.Numeric(precision=6, scale=2), nullable=False, server_default="0.00"),
    )
    op.add_column("works", sa.Column("labor_cost", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"))

    op.create_index(op.f("ix_works_closed_at"), "works", ["closed_at"], unique=False)
    op.create_index(op.f("ix_works_doctor_name"), "works", ["doctor_name"], unique=False)
    op.create_index(op.f("ix_works_patient_name"), "works", ["patient_name"], unique=False)

    op.execute("UPDATE works SET base_price_for_client = price_for_client WHERE base_price_for_client = 0.00")
    op.execute("UPDATE works SET labor_cost = 0.00 WHERE labor_cost IS NULL")

    op.alter_column("clients", "default_price_adjustment_percent", server_default=None)
    op.alter_column("works", "base_price_for_client", server_default=None)
    op.alter_column("works", "price_adjustment_percent", server_default=None)
    op.alter_column("works", "labor_cost", server_default=None)

    op.create_table(
        "work_change_logs",
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("fk_work_change_logs_work_id_works"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_change_logs")),
    )
    op.create_index(op.f("ix_work_change_logs_action"), "work_change_logs", ["action"], unique=False)
    op.create_index(op.f("ix_work_change_logs_work_id"), "work_change_logs", ["work_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_change_logs_work_id"), table_name="work_change_logs")
    op.drop_index(op.f("ix_work_change_logs_action"), table_name="work_change_logs")
    op.drop_table("work_change_logs")

    op.drop_index(op.f("ix_works_patient_name"), table_name="works")
    op.drop_index(op.f("ix_works_doctor_name"), table_name="works")
    op.drop_index(op.f("ix_works_closed_at"), table_name="works")

    op.drop_column("works", "labor_cost")
    op.drop_column("works", "price_adjustment_percent")
    op.drop_column("works", "base_price_for_client")
    op.drop_column("works", "closed_at")
    op.drop_column("works", "tooth_formula")
    op.drop_column("works", "patient_name")
    op.drop_column("works", "doctor_name")

    op.drop_column("clients", "default_price_adjustment_percent")
