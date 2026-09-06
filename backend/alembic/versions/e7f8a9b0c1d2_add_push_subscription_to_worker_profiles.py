"""add_push_subscription_to_worker_profiles

Revision ID: e7f8a9b0c1d2
Revises: 452ce445ecad
Create Date: 2026-09-06 04:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: str | None = "452ce445ecad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.add_column(sa.Column("push_subscription", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.drop_column("push_subscription")
