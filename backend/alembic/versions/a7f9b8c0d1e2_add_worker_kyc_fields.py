"""add_worker_kyc_fields

Revision ID: a7f9b8c0d1e2
Revises: ed113d8a40d4
Create Date: 2026-09-04 18:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7f9b8c0d1e2"
down_revision: str | None = "ed113d8a40d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.add_column(
            sa.Column("father_name", sa.String(length=100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("date_of_birth", sa.String(length=20), nullable=True)
        )
        batch_op.add_column(sa.Column("domicile", sa.String(length=100), nullable=True))
        batch_op.add_column(
            sa.Column("local_address", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("marital_status", sa.String(length=20), nullable=True)
        )
        batch_op.add_column(sa.Column("experience_years", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("languages_spoken", sa.String(length=100), nullable=True)
        )
        batch_op.add_column(
            sa.Column("aadhaar_number", sa.String(length=12), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "police_verification_status",
                sa.String(length=20),
                server_default=sa.text("'pending'"),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "kyc_payment_status",
                sa.String(length=20),
                server_default=sa.text("'pending'"),
                nullable=True,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.drop_column("kyc_payment_status")
        batch_op.drop_column("police_verification_status")
        batch_op.drop_column("aadhaar_number")
        batch_op.drop_column("languages_spoken")
        batch_op.drop_column("experience_years")
        batch_op.drop_column("marital_status")
        batch_op.drop_column("local_address")
        batch_op.drop_column("domicile")
        batch_op.drop_column("date_of_birth")
        batch_op.drop_column("father_name")
