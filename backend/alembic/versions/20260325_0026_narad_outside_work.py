"""narad outside work fields

Revision ID: 20260325_0026
Revises: 20260325_0025
Create Date: 2026-03-25 19:25:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260325_0026"
down_revision = "20260325_0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("narads", sa.Column("is_outside_work", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("narads", sa.Column("outside_lab_name", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("outside_order_number", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("outside_cost", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"))
    op.add_column("narads", sa.Column("outside_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("narads", sa.Column("outside_due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("narads", sa.Column("outside_returned_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("narads", sa.Column("outside_comment", sa.Text(), nullable=True))

    op.create_index(op.f("ix_narads_is_outside_work"), "narads", ["is_outside_work"], unique=False)
    op.create_index(op.f("ix_narads_outside_lab_name"), "narads", ["outside_lab_name"], unique=False)
    op.create_index(op.f("ix_narads_outside_order_number"), "narads", ["outside_order_number"], unique=False)
    op.create_index(op.f("ix_narads_outside_sent_at"), "narads", ["outside_sent_at"], unique=False)
    op.create_index(op.f("ix_narads_outside_due_at"), "narads", ["outside_due_at"], unique=False)
    op.create_index(op.f("ix_narads_outside_returned_at"), "narads", ["outside_returned_at"], unique=False)

    op.alter_column("narads", "is_outside_work", server_default=None)
    op.alter_column("narads", "outside_cost", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_narads_outside_returned_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_outside_due_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_outside_sent_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_outside_order_number"), table_name="narads")
    op.drop_index(op.f("ix_narads_outside_lab_name"), table_name="narads")
    op.drop_index(op.f("ix_narads_is_outside_work"), table_name="narads")

    op.drop_column("narads", "outside_comment")
    op.drop_column("narads", "outside_returned_at")
    op.drop_column("narads", "outside_due_at")
    op.drop_column("narads", "outside_sent_at")
    op.drop_column("narads", "outside_cost")
    op.drop_column("narads", "outside_order_number")
    op.drop_column("narads", "outside_lab_name")
    op.drop_column("narads", "is_outside_work")
