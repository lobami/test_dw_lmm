"""initial migration: create tables and load seed data

Revision ID: 0001_initial
Revises: None
Create Date: 2025-11-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # Create tables using SQLAlchemy metadata to ensure the schema matches models
    from app.database import Base
    Base.metadata.create_all(bind=bind)


def downgrade():
    # Drop all tables created by models (useful for dev only)
    bind = op.get_bind()
    from app.database import Base
    Base.metadata.drop_all(bind=bind)
