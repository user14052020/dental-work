"""Remove duplicated patient fields from works.

Revision ID: 20260324_0020
Revises: 20260324_0019
Create Date: 2026-03-24 21:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260324_0020"
down_revision = "20260324_0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE narads
        SET patient_name = source.patient_name
        FROM (
            SELECT narad_id, max(patient_name) AS patient_name
            FROM works
            WHERE patient_name IS NOT NULL
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.patient_name IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET patient_age = source.patient_age
        FROM (
            SELECT narad_id, max(patient_age) AS patient_age
            FROM works
            WHERE patient_age IS NOT NULL
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.patient_age IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET patient_gender = source.patient_gender
        FROM (
            SELECT narad_id, max(patient_gender) AS patient_gender
            FROM works
            WHERE patient_gender IS NOT NULL
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.patient_gender IS NULL
        """
    )

    op.drop_column("works", "patient_name")
    op.drop_column("works", "patient_age")
    op.drop_column("works", "patient_gender")


def downgrade() -> None:
    op.add_column("works", sa.Column("patient_gender", sa.String(length=16), nullable=True))
    op.add_column("works", sa.Column("patient_age", sa.Integer(), nullable=True))
    op.add_column("works", sa.Column("patient_name", sa.String(length=255), nullable=True))

    op.execute(
        """
        UPDATE works
        SET patient_name = narads.patient_name,
            patient_age = narads.patient_age,
            patient_gender = narads.patient_gender
        FROM narads
        WHERE works.narad_id = narads.id
        """
    )
