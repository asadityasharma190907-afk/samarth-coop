"""story_17_3_gender_fields

Revision ID: e1f2a3b4c5d6
Revises: 452ce445ecad
Create Date: 2026-09-06 04:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: str | None = "452ce445ecad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "worker_profiles",
        sa.Column(
            "gender",
            sa.String(length=20),
            nullable=False,
            server_default="prefer_not_to_say",
        ),
    )
    op.add_column(
        "bookings",
        sa.Column(
            "gender_preference",
            sa.String(length=20),
            nullable=False,
            server_default="any",
        ),
    )


def downgrade() -> None:
    op.drop_column("bookings", "gender_preference")
    op.drop_column("worker_profiles", "gender")
