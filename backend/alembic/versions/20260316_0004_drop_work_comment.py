"""drop work comment

Revision ID: 20260316_0004
Revises: 20260316_0003
Create Date: 2026-03-16 23:55:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260316_0004"
down_revision = "20260316_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("works", "comment")


def downgrade() -> None:
    op.add_column("works", sa.Column("comment", sa.Text(), nullable=True))
