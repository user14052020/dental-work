"""add delivery fields

Revision ID: 20260317_0011
Revises: 20260317_0010
Create Date: 2026-03-17 23:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0011"
down_revision = "20260317_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("delivery_address", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("delivery_contact", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("delivery_phone", sa.String(length=20), nullable=True))

    op.add_column(
        "works",
        sa.Column("delivery_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("works", sa.Column("delivery_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_works_delivery_sent"), "works", ["delivery_sent"], unique=False)
    op.create_index(op.f("ix_works_delivery_sent_at"), "works", ["delivery_sent_at"], unique=False)
    op.alter_column("works", "delivery_sent", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_works_delivery_sent_at"), table_name="works")
    op.drop_index(op.f("ix_works_delivery_sent"), table_name="works")
    op.drop_column("works", "delivery_sent_at")
    op.drop_column("works", "delivery_sent")
    op.drop_column("clients", "delivery_phone")
    op.drop_column("clients", "delivery_contact")
    op.drop_column("clients", "delivery_address")
