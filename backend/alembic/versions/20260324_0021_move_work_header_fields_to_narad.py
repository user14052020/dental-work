"""Move work header fields to narads.

Revision ID: 20260324_0021
Revises: 20260324_0020
Create Date: 2026-03-24 23:35:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260324_0021"
down_revision = "20260324_0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("narads", sa.Column("require_color_photo", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("narads", sa.Column("face_shape", sa.String(length=32), nullable=True))
    op.add_column("narads", sa.Column("implant_system", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("metal_type", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("shade_color", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("tooth_formula", sa.String(length=255), nullable=True))
    op.add_column("narads", sa.Column("tooth_selection", sa.JSON(), nullable=True))

    op.execute(
        """
        UPDATE narads
        SET require_color_photo = source.require_color_photo
        FROM (
            SELECT narad_id, bool_or(require_color_photo) AS require_color_photo
            FROM works
            GROUP BY narad_id
        ) AS source
        WHERE narads.id = source.narad_id
        """
    )
    op.execute(
        """
        UPDATE narads
        SET face_shape = source.face_shape
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, face_shape
            FROM works
            WHERE face_shape IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.face_shape IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET implant_system = source.implant_system
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, implant_system
            FROM works
            WHERE implant_system IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.implant_system IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET metal_type = source.metal_type
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, metal_type
            FROM works
            WHERE metal_type IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.metal_type IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET shade_color = source.shade_color
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, shade_color
            FROM works
            WHERE shade_color IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.shade_color IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET tooth_formula = source.tooth_formula
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, tooth_formula
            FROM works
            WHERE tooth_formula IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.tooth_formula IS NULL
        """
    )
    op.execute(
        """
        UPDATE narads
        SET tooth_selection = source.tooth_selection
        FROM (
            SELECT DISTINCT ON (narad_id) narad_id, tooth_selection
            FROM works
            WHERE tooth_selection IS NOT NULL
            ORDER BY narad_id, updated_at DESC, created_at DESC
        ) AS source
        WHERE narads.id = source.narad_id
          AND narads.tooth_selection IS NULL
        """
    )

    op.alter_column("narads", "require_color_photo", server_default=None)

    op.drop_column("works", "require_color_photo")
    op.drop_column("works", "face_shape")
    op.drop_column("works", "implant_system")
    op.drop_column("works", "metal_type")
    op.drop_column("works", "shade_color")
    op.drop_column("works", "tooth_formula")
    op.drop_column("works", "tooth_selection")


def downgrade() -> None:
    op.add_column("works", sa.Column("tooth_selection", sa.JSON(), nullable=True))
    op.add_column("works", sa.Column("tooth_formula", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("shade_color", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("metal_type", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("implant_system", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("face_shape", sa.String(length=32), nullable=True))
    op.add_column("works", sa.Column("require_color_photo", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.execute(
        """
        UPDATE works
        SET require_color_photo = narads.require_color_photo,
            face_shape = narads.face_shape,
            implant_system = narads.implant_system,
            metal_type = narads.metal_type,
            shade_color = narads.shade_color,
            tooth_formula = narads.tooth_formula,
            tooth_selection = narads.tooth_selection
        FROM narads
        WHERE works.narad_id = narads.id
        """
    )

    op.alter_column("works", "require_color_photo", server_default=None)

    op.drop_column("narads", "tooth_selection")
    op.drop_column("narads", "tooth_formula")
    op.drop_column("narads", "shade_color")
    op.drop_column("narads", "metal_type")
    op.drop_column("narads", "implant_system")
    op.drop_column("narads", "face_shape")
    op.drop_column("narads", "require_color_photo")
