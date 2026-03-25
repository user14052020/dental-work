"""contractors directory and narad contractor link

Revision ID: 20260325_0027
Revises: 20260325_0026
Create Date: 2026-03-25 23:10:00.000000
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "20260325_0027"
down_revision = "20260325_0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contractors",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contractors_name"), "contractors", ["name"], unique=False)
    op.create_index(op.f("ix_contractors_phone"), "contractors", ["phone"], unique=False)
    op.create_index(op.f("ix_contractors_email"), "contractors", ["email"], unique=False)
    op.create_index(op.f("ix_contractors_is_active"), "contractors", ["is_active"], unique=False)
    op.add_column("narads", sa.Column("contractor_id", sa.UUID(), nullable=True))
    op.create_index(op.f("ix_narads_contractor_id"), "narads", ["contractor_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_narads_contractor_id_contractors"),
        "narads",
        "contractors",
        ["contractor_id"],
        ["id"],
        ondelete="SET NULL",
    )

    bind = op.get_bind()
    existing_names = [
        row[0]
        for row in bind.execute(
            sa.text(
                """
                SELECT DISTINCT outside_lab_name
                FROM narads
                WHERE outside_lab_name IS NOT NULL AND btrim(outside_lab_name) <> ''
                """
            )
        ).fetchall()
    ]
    now = datetime.now(timezone.utc)
    for name in existing_names:
        contractor_id = uuid4()
        bind.execute(
            sa.text(
                """
                INSERT INTO contractors (id, created_at, updated_at, name, is_active)
                VALUES (:id, :created_at, :updated_at, :name, :is_active)
                """
            ),
            {
                "id": contractor_id,
                "created_at": now,
                "updated_at": now,
                "name": name,
                "is_active": True,
            },
        )
        bind.execute(
            sa.text(
                """
                UPDATE narads
                SET contractor_id = :contractor_id
                WHERE contractor_id IS NULL AND outside_lab_name = :name
                """
            ),
            {"contractor_id": contractor_id, "name": name},
        )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_narads_contractor_id_contractors"), "narads", type_="foreignkey")
    op.drop_index(op.f("ix_narads_contractor_id"), table_name="narads")
    op.drop_column("narads", "contractor_id")
    op.drop_index(op.f("ix_contractors_is_active"), table_name="contractors")
    op.drop_index(op.f("ix_contractors_email"), table_name="contractors")
    op.drop_index(op.f("ix_contractors_phone"), table_name="contractors")
    op.drop_index(op.f("ix_contractors_name"), table_name="contractors")
    op.drop_table("contractors")
