"""payments module

Revision ID: 20260324_0015
Revises: 20260317_0014
Create Date: 2026-03-24 16:30:00.000000
"""

from __future__ import annotations

from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260324_0015"
down_revision = "20260317_0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
        sa.UniqueConstraint("payment_number", name=op.f("uq_payments_payment_number")),
    )
    op.create_index(op.f("ix_payments_payment_number"), "payments", ["payment_number"], unique=False)
    op.create_index(op.f("ix_payments_client_id"), "payments", ["client_id"], unique=False)
    op.create_index(op.f("ix_payments_payment_date"), "payments", ["payment_date"], unique=False)
    op.create_index(op.f("ix_payments_method"), "payments", ["method"], unique=False)
    op.create_index(op.f("ix_payments_external_reference"), "payments", ["external_reference"], unique=False)

    op.create_table(
        "payment_allocations",
        sa.Column("payment_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("work_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payment_allocations")),
        sa.UniqueConstraint("payment_id", "work_id", name="uq_payment_allocations_payment_work"),
    )
    op.create_index(op.f("ix_payment_allocations_payment_id"), "payment_allocations", ["payment_id"], unique=False)
    op.create_index(op.f("ix_payment_allocations_work_id"), "payment_allocations", ["work_id"], unique=False)

    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            SELECT id, client_id, order_number, amount_paid, created_at, updated_at
            FROM works
            WHERE amount_paid > 0
            """
        )
    ).mappings()

    for row in rows:
        payment_id = str(uuid4())
        allocation_id = str(uuid4())
        payment_number = f"LEGACY-{row['order_number']}"
        payment_date = row["updated_at"] or row["created_at"]
        amount_paid = row["amount_paid"]
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        bind.execute(
            sa.text(
                """
                INSERT INTO payments (
                    id,
                    payment_number,
                    client_id,
                    payment_date,
                    method,
                    amount,
                    external_reference,
                    comment,
                    created_at,
                    updated_at
                ) VALUES (
                    :id,
                    :payment_number,
                    :client_id,
                    :payment_date,
                    :method,
                    :amount,
                    NULL,
                    :comment,
                    :created_at,
                    :updated_at
                )
                """
            ),
            {
                "id": payment_id,
                "payment_number": payment_number,
                "client_id": row["client_id"],
                "payment_date": payment_date,
                "method": "bank_transfer",
                "amount": amount_paid,
                "comment": "Импортировано из legacy amount_paid",
                "created_at": created_at,
                "updated_at": updated_at,
            },
        )
        bind.execute(
            sa.text(
                """
                INSERT INTO payment_allocations (
                    id,
                    payment_id,
                    work_id,
                    amount,
                    created_at,
                    updated_at
                ) VALUES (
                    :id,
                    :payment_id,
                    :work_id,
                    :amount,
                    :created_at,
                    :updated_at
                )
                """
            ),
            {
                "id": allocation_id,
                "payment_id": payment_id,
                "work_id": row["id"],
                "amount": amount_paid,
                "created_at": created_at,
                "updated_at": updated_at,
            },
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_allocations_work_id"), table_name="payment_allocations")
    op.drop_index(op.f("ix_payment_allocations_payment_id"), table_name="payment_allocations")
    op.drop_table("payment_allocations")

    op.drop_index(op.f("ix_payments_external_reference"), table_name="payments")
    op.drop_index(op.f("ix_payments_method"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_date"), table_name="payments")
    op.drop_index(op.f("ix_payments_client_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_payment_number"), table_name="payments")
    op.drop_table("payments")
