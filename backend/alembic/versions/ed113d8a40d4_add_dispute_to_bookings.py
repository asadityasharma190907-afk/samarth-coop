"""add_dispute_to_bookings

Revision ID: ed113d8a40d4
Revises: '23b55611e66d'
Create Date: 2026-09-03 17:28:35.945473

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ed113d8a40d4"
down_revision: str | None = "23b55611e66d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.add_column(
            sa.Column("dispute_reason", sa.String(length=500), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.drop_column("dispute_reason")
