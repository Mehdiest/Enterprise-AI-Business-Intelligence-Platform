"""Add conversation memory table.

Revision ID: 003
Revises: 002
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the conversation_turns table backing persistent Copilot memory."""
    op.create_table(
        "conversation_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conversation_turns_session_id",
        "conversation_turns",
        ["session_id"],
    )
    op.create_index(
        "ix_conversation_turns_expires_at",
        "conversation_turns",
        ["expires_at"],
    )


def downgrade() -> None:
    """Drop the conversation memory table."""
    op.drop_index("ix_conversation_turns_expires_at", table_name="conversation_turns")
    op.drop_index("ix_conversation_turns_session_id", table_name="conversation_turns")
    op.drop_table("conversation_turns")