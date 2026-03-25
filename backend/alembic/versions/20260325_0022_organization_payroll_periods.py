"""Add payroll period settings to organization profile.

Revision ID: 20260325_0022
Revises: 20260324_0021
Create Date: 2026-03-25 12:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260325_0022"
down_revision = "20260324_0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organization_profiles",
        sa.Column("payroll_period_start_days", sa.JSON(), nullable=False, server_default=sa.text("'[1]'::json")),
    )
    op.alter_column("organization_profiles", "payroll_period_start_days", server_default=None)


def downgrade() -> None:
    op.drop_column("organization_profiles", "payroll_period_start_days")
