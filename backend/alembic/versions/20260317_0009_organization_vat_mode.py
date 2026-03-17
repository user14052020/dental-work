"""add vat mode for organization profile

Revision ID: 20260317_0009
Revises: 20260317_0008
Create Date: 2026-03-17 18:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0009"
down_revision = "20260317_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organization_profiles",
        sa.Column("vat_mode", sa.String(length=32), nullable=False, server_default="without_vat"),
    )
    op.execute(
        """
        UPDATE organization_profiles
        SET vat_mode = CASE
            WHEN vat_label ILIKE '%20%' THEN 'vat_20'
            WHEN vat_label ILIKE '%10%' THEN 'vat_10'
            WHEN vat_label ILIKE '%7%' THEN 'vat_7'
            WHEN vat_label ILIKE '%5%' THEN 'vat_5'
            WHEN vat_label ILIKE '%0%' THEN 'vat_0'
            ELSE 'without_vat'
        END
        """
    )
    op.alter_column("organization_profiles", "vat_mode", server_default=None)


def downgrade() -> None:
    op.drop_column("organization_profiles", "vat_mode")
