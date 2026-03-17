"""add work tooth selection

Revision ID: 20260316_0005
Revises: 20260316_0004
Create Date: 2026-03-16 23:59:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260316_0005"
down_revision = "20260316_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("works", sa.Column("tooth_selection", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("works", "tooth_selection")
