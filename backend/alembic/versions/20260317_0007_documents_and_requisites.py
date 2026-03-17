"""documents and requisites

Revision ID: 20260317_0007
Revises: 20260317_0006
Create Date: 2026-03-17 01:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0007"
down_revision = "20260317_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organization_profiles",
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("short_name", sa.String(length=255), nullable=True),
        sa.Column("legal_address", sa.String(length=255), nullable=True),
        sa.Column("mailing_address", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("inn", sa.String(length=20), nullable=True),
        sa.Column("kpp", sa.String(length=20), nullable=True),
        sa.Column("ogrn", sa.String(length=30), nullable=True),
        sa.Column("bank_name", sa.String(length=255), nullable=True),
        sa.Column("bik", sa.String(length=20), nullable=True),
        sa.Column("settlement_account", sa.String(length=30), nullable=True),
        sa.Column("correspondent_account", sa.String(length=30), nullable=True),
        sa.Column("recipient_name", sa.String(length=255), nullable=True),
        sa.Column("director_name", sa.String(length=255), nullable=True),
        sa.Column("accountant_name", sa.String(length=255), nullable=True),
        sa.Column("vat_label", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("clients", sa.Column("legal_name", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("legal_address", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("inn", sa.String(length=20), nullable=True))
    op.add_column("clients", sa.Column("kpp", sa.String(length=20), nullable=True))
    op.add_column("clients", sa.Column("ogrn", sa.String(length=30), nullable=True))
    op.add_column("clients", sa.Column("bank_name", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("bik", sa.String(length=20), nullable=True))
    op.add_column("clients", sa.Column("settlement_account", sa.String(length=30), nullable=True))
    op.add_column("clients", sa.Column("correspondent_account", sa.String(length=30), nullable=True))
    op.add_column("clients", sa.Column("contract_number", sa.String(length=100), nullable=True))
    op.add_column("clients", sa.Column("contract_date", sa.Date(), nullable=True))
    op.add_column("clients", sa.Column("signer_name", sa.String(length=255), nullable=True))
    op.create_index("ix_clients_inn", "clients", ["inn"], unique=False)

    op.add_column("works", sa.Column("doctor_phone", sa.String(length=20), nullable=True))
    op.add_column("works", sa.Column("patient_age", sa.Integer(), nullable=True))
    op.add_column("works", sa.Column("patient_gender", sa.String(length=16), nullable=True))
    op.add_column("works", sa.Column("require_color_photo", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("works", sa.Column("face_shape", sa.String(length=32), nullable=True))
    op.add_column("works", sa.Column("implant_system", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("metal_type", sa.String(length=255), nullable=True))
    op.add_column("works", sa.Column("shade_color", sa.String(length=255), nullable=True))
    op.create_index("ix_works_patient_gender", "works", ["patient_gender"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_works_patient_gender", table_name="works")
    op.drop_column("works", "shade_color")
    op.drop_column("works", "metal_type")
    op.drop_column("works", "implant_system")
    op.drop_column("works", "face_shape")
    op.drop_column("works", "require_color_photo")
    op.drop_column("works", "patient_gender")
    op.drop_column("works", "patient_age")
    op.drop_column("works", "doctor_phone")

    op.drop_index("ix_clients_inn", table_name="clients")
    op.drop_column("clients", "signer_name")
    op.drop_column("clients", "contract_date")
    op.drop_column("clients", "contract_number")
    op.drop_column("clients", "correspondent_account")
    op.drop_column("clients", "settlement_account")
    op.drop_column("clients", "bik")
    op.drop_column("clients", "bank_name")
    op.drop_column("clients", "ogrn")
    op.drop_column("clients", "kpp")
    op.drop_column("clients", "inn")
    op.drop_column("clients", "legal_address")
    op.drop_column("clients", "legal_name")

    op.drop_table("organization_profiles")
