"""organization smtp settings

Revision ID: 20260325_0024
Revises: 20260325_0023
Create Date: 2026-03-25 12:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260325_0024"
down_revision = "20260325_0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organization_profiles", sa.Column("smtp_host", sa.String(length=255), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_port", sa.Integer(), nullable=False, server_default="587"))
    op.add_column("organization_profiles", sa.Column("smtp_username", sa.String(length=255), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_password", sa.Text(), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_from_email", sa.String(length=255), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_from_name", sa.String(length=255), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_reply_to", sa.String(length=255), nullable=True))
    op.add_column("organization_profiles", sa.Column("smtp_use_tls", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("organization_profiles", sa.Column("smtp_use_ssl", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("organization_profiles", "smtp_port", server_default=None)
    op.alter_column("organization_profiles", "smtp_use_tls", server_default=None)
    op.alter_column("organization_profiles", "smtp_use_ssl", server_default=None)


def downgrade() -> None:
    op.drop_column("organization_profiles", "smtp_use_ssl")
    op.drop_column("organization_profiles", "smtp_use_tls")
    op.drop_column("organization_profiles", "smtp_reply_to")
    op.drop_column("organization_profiles", "smtp_from_name")
    op.drop_column("organization_profiles", "smtp_from_email")
    op.drop_column("organization_profiles", "smtp_password")
    op.drop_column("organization_profiles", "smtp_username")
    op.drop_column("organization_profiles", "smtp_port")
    op.drop_column("organization_profiles", "smtp_host")
