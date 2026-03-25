"""narads module

Revision ID: 20260324_0016
Revises: 20260324_0015
Create Date: 2026-03-24 19:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260324_0016"
down_revision = "20260324_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "narads",
        sa.Column("narad_number", sa.String(length=50), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("doctor_name", sa.String(length=255), nullable=True),
        sa.Column("doctor_phone", sa.String(length=20), nullable=True),
        sa.Column("patient_name", sa.String(length=255), nullable=True),
        sa.Column("patient_age", sa.Integer(), nullable=True),
        sa.Column("patient_gender", sa.String(length=16), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_narads")),
        sa.UniqueConstraint("narad_number", name=op.f("uq_narads_narad_number")),
    )
    op.create_index(op.f("ix_narads_narad_number"), "narads", ["narad_number"], unique=False)
    op.create_index(op.f("ix_narads_client_id"), "narads", ["client_id"], unique=False)
    op.create_index(op.f("ix_narads_doctor_id"), "narads", ["doctor_id"], unique=False)
    op.create_index(op.f("ix_narads_title"), "narads", ["title"], unique=False)
    op.create_index(op.f("ix_narads_doctor_name"), "narads", ["doctor_name"], unique=False)
    op.create_index(op.f("ix_narads_patient_name"), "narads", ["patient_name"], unique=False)
    op.create_index(op.f("ix_narads_patient_gender"), "narads", ["patient_gender"], unique=False)
    op.create_index(op.f("ix_narads_status"), "narads", ["status"], unique=False)
    op.create_index(op.f("ix_narads_received_at"), "narads", ["received_at"], unique=False)
    op.create_index(op.f("ix_narads_deadline_at"), "narads", ["deadline_at"], unique=False)
    op.create_index(op.f("ix_narads_closed_at"), "narads", ["closed_at"], unique=False)

    op.create_table(
        "narad_status_logs",
        sa.Column("narad_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["narad_id"], ["narads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_narad_status_logs")),
    )
    op.create_index(op.f("ix_narad_status_logs_narad_id"), "narad_status_logs", ["narad_id"], unique=False)
    op.create_index(op.f("ix_narad_status_logs_action"), "narad_status_logs", ["action"], unique=False)
    op.create_index(op.f("ix_narad_status_logs_to_status"), "narad_status_logs", ["to_status"], unique=False)

    op.add_column("works", sa.Column("narad_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.create_index(op.f("ix_works_narad_id"), "works", ["narad_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_works_narad_id_narads"),
        "works",
        "narads",
        ["narad_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        INSERT INTO narads (
            narad_number,
            client_id,
            doctor_id,
            title,
            description,
            doctor_name,
            doctor_phone,
            patient_name,
            patient_age,
            patient_gender,
            status,
            received_at,
            deadline_at,
            completed_at,
            closed_at,
            id,
            created_at,
            updated_at
        )
        SELECT
            works.order_number,
            works.client_id,
            works.doctor_id,
            works.work_type,
            works.description,
            works.doctor_name,
            works.doctor_phone,
            works.patient_name,
            works.patient_age,
            works.patient_gender,
            works.status,
            works.received_at,
            works.deadline_at,
            works.completed_at,
            works.closed_at,
            works.id,
            works.created_at,
            works.updated_at
        FROM works
        """
    )
    op.execute("UPDATE works SET narad_id = id WHERE narad_id IS NULL")
    op.execute(
        """
        INSERT INTO narad_status_logs (
            narad_id,
            action,
            actor_email,
            from_status,
            to_status,
            note,
            details,
            id,
            created_at,
            updated_at
        )
        SELECT
            works.id,
            'migrated',
            NULL,
            NULL,
            works.status,
            NULL,
            jsonb_build_object('source', 'works_migration', 'order_number', works.order_number),
            works.id,
            works.created_at,
            works.updated_at
        FROM works
        """
    )
    op.alter_column("works", "narad_id", nullable=False)
    op.alter_column("narads", "status", server_default=None)
    op.alter_column("narad_status_logs", "details", server_default=None)


def downgrade() -> None:
    op.drop_constraint(op.f("fk_works_narad_id_narads"), "works", type_="foreignkey")
    op.drop_index(op.f("ix_works_narad_id"), table_name="works")
    op.drop_column("works", "narad_id")

    op.drop_index(op.f("ix_narad_status_logs_to_status"), table_name="narad_status_logs")
    op.drop_index(op.f("ix_narad_status_logs_action"), table_name="narad_status_logs")
    op.drop_index(op.f("ix_narad_status_logs_narad_id"), table_name="narad_status_logs")
    op.drop_table("narad_status_logs")

    op.drop_index(op.f("ix_narads_closed_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_deadline_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_received_at"), table_name="narads")
    op.drop_index(op.f("ix_narads_status"), table_name="narads")
    op.drop_index(op.f("ix_narads_patient_gender"), table_name="narads")
    op.drop_index(op.f("ix_narads_patient_name"), table_name="narads")
    op.drop_index(op.f("ix_narads_doctor_name"), table_name="narads")
    op.drop_index(op.f("ix_narads_title"), table_name="narads")
    op.drop_index(op.f("ix_narads_doctor_id"), table_name="narads")
    op.drop_index(op.f("ix_narads_client_id"), table_name="narads")
    op.drop_index(op.f("ix_narads_narad_number"), table_name="narads")
    op.drop_table("narads")
