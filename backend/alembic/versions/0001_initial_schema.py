"""initial_schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-31 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure pgcrypto extension for gen_random_uuid() if postgres
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # 1. users
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(length=15), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
        sa.CheckConstraint(
            "role IN ('citizen', 'worker', 'admin')", name="ck_users_role"
        ),
    )
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)

    # 2. worker_profiles
    op.create_table(
        "worker_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill", sa.String(length=50), nullable=False),
        sa.Column("lat", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("lng", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=True),
        sa.Column(
            "availability", sa.Boolean(), server_default=sa.text("TRUE"), nullable=True
        ),
        sa.Column(
            "verified", sa.Boolean(), server_default=sa.text("FALSE"), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # 3. bookings
    op.create_table(
        "bookings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("citizen_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("skill", sa.String(length=50), nullable=False),
        sa.Column("lat", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("lng", sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("job_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("platform_fee", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["citizen_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["worker_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending', 'assigned', 'completed', 'cancelled')",
            name="ck_bookings_status",
        ),
    )

    # 4. booking_offers
    op.create_table(
        "booking_offers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rank_at_offer", sa.Integer(), nullable=False),
        sa.Column("dispatch_score", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'offered'"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.ForeignKeyConstraint(["worker_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('offered', 'accepted', 'declined', 'expired')",
            name="ck_booking_offers_status",
        ),
    )


def downgrade() -> None:
    op.drop_table("booking_offers")
    op.drop_table("bookings")
    op.drop_table("worker_profiles")
    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_table("users")
