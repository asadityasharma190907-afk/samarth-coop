"""create_welfare_disbursements_table

Revision ID: b9f4a1c2d3e4
Revises: 9657aff49c07, a7f9b8c0d1e2
Create Date: 2026-09-06 03:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9f4a1c2d3e4"
down_revision: str | Sequence[str] | None = ("9657aff49c07", "a7f9b8c0d1e2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "welfare_disbursements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("disbursed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "disbursed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["disbursed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "category IN ('insurance', 'tool_loan', 'training', 'emergency', 'pension')",
            name="ck_welfare_disbursements_category",
        ),
    )


def downgrade() -> None:
    op.drop_table("welfare_disbursements")
