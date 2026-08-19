"""Add refresh token rotation columns to users.

Revision ID: 002
Revises: 001
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the columns that store the active refresh token."""
    op.add_column(
        "users",
        sa.Column("refresh_token_jti", sa.String(length=36), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_users_refresh_token_jti",
        "users",
        ["refresh_token_jti"],
    )


def downgrade() -> None:
    """Remove the refresh token rotation columns."""
    op.drop_index("ix_users_refresh_token_jti", table_name="users")
    op.drop_column("users", "refresh_token_hash")
    op.drop_column("users", "refresh_token_jti")
