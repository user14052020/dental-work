"""Add employees and permission fields to users.

Revision ID: 20260325_0023
Revises: 20260325_0022
Create Date: 2026-03-25 15:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260325_0023"
down_revision = "20260325_0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("job_title", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("is_fired", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column(
        "users",
        sa.Column("permission_codes", sa.JSON(), nullable=False, server_default=sa.text("'[\"*\"]'::json")),
    )
    op.add_column("users", sa.Column("executor_id", sa.UUID(as_uuid=False), nullable=True))

    op.execute(
        """
        UPDATE users
        SET full_name = CASE
            WHEN split_part(email, '@', 1) = '' THEN email
            ELSE split_part(email, '@', 1)
        END
        WHERE full_name IS NULL
        """
    )

    op.alter_column("users", "full_name", nullable=False)
    op.create_index("ix_users_full_name", "users", ["full_name"], unique=False)
    op.create_index("ix_users_is_fired", "users", ["is_fired"], unique=False)
    op.create_index("ix_users_executor_id", "users", ["executor_id"], unique=True)
    op.create_foreign_key(
        "fk_users_executor_id_executors",
        "users",
        "executors",
        ["executor_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("users", "is_fired", server_default=None)
    op.alter_column("users", "permission_codes", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_users_executor_id_executors", "users", type_="foreignkey")
    op.drop_index("ix_users_executor_id", table_name="users")
    op.drop_index("ix_users_is_fired", table_name="users")
    op.drop_index("ix_users_full_name", table_name="users")
    op.drop_column("users", "executor_id")
    op.drop_column("users", "permission_codes")
    op.drop_column("users", "is_fired")
    op.drop_column("users", "job_title")
    op.drop_column("users", "phone")
    op.drop_column("users", "full_name")
