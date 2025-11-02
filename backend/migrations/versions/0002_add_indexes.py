"""add indexes for users.email and refresh_tokens.token

Revision ID: 0002_add_indexes
Revises: 0001_initial
Create Date: 2025-11-01 00:10:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_indexes'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Create an index on refresh_tokens.token to speed lookups and enforce uniqueness
    # if not already present. Use try/except to be resilient across DBs.
    try:
        op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=False)
    except Exception:
        pass

    # Ensure users.email has an index/constraint. The model declares unique=True,
    # but make sure an index exists for performance.
    try:
        op.create_index('ix_users_email', 'users', ['email'], unique=False)
    except Exception:
        pass


def downgrade():
    try:
        op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    except Exception:
        pass
    try:
        op.drop_index('ix_users_email', table_name='users')
    except Exception:
        pass
