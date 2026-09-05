"""merge_heads

Revision ID: ec519d3c7c9c
Revises: "('9657aff49c07', 'a7f9b8c0d1e2')"
Create Date: 2026-09-06 02:58:32.361742

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "ec519d3c7c9c"
down_revision: str | None = ("9657aff49c07", "a7f9b8c0d1e2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
