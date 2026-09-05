"""story_13_2_add_pricing_columns_to_bookings

Revision ID: 9657aff49c07
Revises: ed113d8a40d4
Create Date: 2026-09-06 01:22:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9657aff49c07"
down_revision: str | None = "ed113d8a40d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.add_column(
            sa.Column("base_price", sa.Numeric(precision=10, scale=2), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "surge_surplus",
                sa.Numeric(precision=10, scale=2),
                nullable=True,
                server_default="0",
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_surging",
                sa.Boolean(),
                nullable=True,
                server_default="FALSE",
            )
        )
        batch_op.add_column(
            sa.Column(
                "urgency",
                sa.String(length=20),
                nullable=True,
                server_default="normal",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.drop_column("urgency")
        batch_op.drop_column("is_surging")
        batch_op.drop_column("surge_surplus")
        batch_op.drop_column("base_price")
