"""story_17_5_photo_urls

Revision ID: f1a2b3c4d5e6
Revises: e1f2a3b4c5d6
Create Date: 2026-09-06 04:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "e1f2a3b4c5d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("before_photo_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "bookings",
        sa.Column("after_photo_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bookings", "after_photo_url")
    op.drop_column("bookings", "before_photo_url")
