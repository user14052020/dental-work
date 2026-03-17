"""fix organization profile id type

Revision ID: 20260317_0008
Revises: 20260317_0007
Create Date: 2026-03-17 16:40:00
"""

from alembic import op
from sqlalchemy.dialects import postgresql


revision = "20260317_0008"
down_revision = "20260317_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "organization_profiles",
        "id",
        existing_type=postgresql.VARCHAR(length=36),
        type_=postgresql.UUID(as_uuid=False),
        postgresql_using="id::uuid",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "organization_profiles",
        "id",
        existing_type=postgresql.UUID(as_uuid=False),
        type_=postgresql.VARCHAR(length=36),
        postgresql_using="id::text",
        existing_nullable=False,
    )
