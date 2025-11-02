"""add unique constraint for users.email

Revision ID: 0003_users_email_unique
Revises: 0002_add_indexes
Create Date: 2025-11-01 00:20:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_users_email_unique'
down_revision = '0002_add_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Add unique constraint to users.email if not present.
    try:
        op.create_unique_constraint('uq_users_email', 'users', ['email'])
    except Exception:
        # Some DBs may already enforce uniqueness via model; ignore errors
        pass


def downgrade():
    try:
        op.drop_constraint('uq_users_email', 'users', type_='unique')
    except Exception:
        pass
