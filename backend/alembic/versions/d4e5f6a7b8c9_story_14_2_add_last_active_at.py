"""story_14_2_add_last_active_at_to_worker_profiles

Revision ID: d4e5f6a7b8c9
Revises: 9657aff49c07
Create Date: 2026-09-06 02:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "9657aff49c07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.add_column(
            sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("worker_profiles") as batch_op:
        batch_op.drop_column("last_active_at")
