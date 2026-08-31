"""story_5_2_rating_api

Revision ID: c56d8283c0f0
Revises: '0001_initial_schema'
Create Date: 2026-09-01 02:50:27.851793

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c56d8283c0f0"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "worker_profiles",
        sa.Column(
            "rating_count", sa.Integer(), server_default=sa.text("0"), nullable=True
        ),
    )
    op.add_column("bookings", sa.Column("rating", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("bookings", "rating")
    op.drop_column("worker_profiles", "rating_count")
