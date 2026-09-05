"""story_15_1_citizen_trust_score

Revision ID: 452ce445ecad
Revises: 'ec519d3c7c9c'
Create Date: 2026-09-06 02:59:25.753140

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "452ce445ecad"
down_revision: str | None = "b9f4a1c2d3e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "cancellation_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "citizen_trust_score", sa.Integer(), nullable=False, server_default="100"
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "citizen_trust_score")
    op.drop_column("users", "cancellation_count")
