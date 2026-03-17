"""add work attachments

Revision ID: 20260317_0010
Revises: 20260317_0009
Create Date: 2026-03-17 19:20:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260317_0010"
down_revision = "20260317_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_attachments",
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_email", sa.String(length=255), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("fk_work_attachments_work_id_works"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_attachments")),
        sa.UniqueConstraint("storage_key", name=op.f("uq_work_attachments_storage_key")),
    )
    op.create_index(op.f("ix_work_attachments_work_id"), "work_attachments", ["work_id"], unique=False)
    op.create_index(op.f("ix_work_attachments_file_size"), "work_attachments", ["file_size"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_work_attachments_file_size"), table_name="work_attachments")
    op.drop_index(op.f("ix_work_attachments_work_id"), table_name="work_attachments")
    op.drop_table("work_attachments")
