"""add_verification_status

Revision ID: 23b55611e66d
Revises: 'c56d8283c0f0'
Create Date: 2026-09-03 14:11:36.814279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23b55611e66d'
down_revision: Union[str, None] = 'c56d8283c0f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the new column
    op.add_column('worker_profiles', sa.Column('verification_status', sa.String(length=20), server_default=sa.text("'pending'"), nullable=True))
    
    # 2. Migrate existing data
    # SQLite uses 1/0 or TRUE/FALSE. Using TRUE/FALSE as text or 1/0 depends on dialect, but SQLAlchemy execute can handle basic string.
    # To be fully cross-dialect, we can just run two updates:
    op.execute("UPDATE worker_profiles SET verification_status = 'verified' WHERE verified = TRUE OR verified = 1")
    op.execute("UPDATE worker_profiles SET verification_status = 'pending' WHERE verified = FALSE OR verified = 0 OR verified IS NULL")
    
    # 3. Drop the old column using batch_alter_table (required for SQLite)
    with op.batch_alter_table('worker_profiles') as batch_op:
        batch_op.drop_column('verified')

def downgrade() -> None:
    # 1. Add back the old column
    op.add_column('worker_profiles', sa.Column('verified', sa.Boolean(), server_default=sa.text("FALSE"), nullable=True))
    
    # 2. Restore existing data
    op.execute("UPDATE worker_profiles SET verified = TRUE WHERE verification_status = 'verified'")
    op.execute("UPDATE worker_profiles SET verified = FALSE WHERE verification_status != 'verified'")
    
    # 3. Drop the new column using batch_alter_table
    with op.batch_alter_table('worker_profiles') as batch_op:
        batch_op.drop_column('verification_status')
