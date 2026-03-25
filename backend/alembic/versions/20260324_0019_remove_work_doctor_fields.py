"""Remove duplicated doctor fields from works.

Revision ID: 20260324_0019
Revises: 20260324_0018
Create Date: 2026-03-24 20:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260324_0019"
down_revision = "20260324_0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE narads
        SET doctor_id = source.doctor_id
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, doctor_id
            FROM works
            WHERE doctor_id IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.doctor_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET doctor_name = source.doctor_name
        FROM (
            SELECT narad_id, max(doctor_name) AS doctor_name
            FROM works
            WHERE doctor_name IS NOT NULL
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.doctor_name IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET doctor_phone = source.doctor_phone
        FROM (
            SELECT narad_id, max(doctor_phone) AS doctor_phone
            FROM works
            WHERE doctor_phone IS NOT NULL
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.doctor_phone IS NULL
        """
    )

    op.drop_constraint("fk_works_doctor_id_doctors", "works", type_="foreignkey")
    op.drop_column("works", "doctor_id")
    op.drop_column("works", "doctor_name")
    op.drop_column("works", "doctor_phone")


def downgrade() -> None:
    op.add_column("works", sa.Column("doctor_phone", sa.String(length=20), nullable=True))
    op.add_column("works", sa.Column("doctor_name", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("doctor_id", sa.UUID(as_uuid=False), nullable=True))
    op.create_foreign_key(
        "fk_works_doctor_id_doctors",
        "works",
        "doctors",
        ["doctor_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        """
        UPDATE works
        SET doctor_id = narads.doctor_id,
            doctor_name = narads.doctor_name,
            doctor_phone = narads.doctor_phone
        FROM narads
        WHERE works.narad_id = narads.id
        """
    )
