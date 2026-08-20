"""Initial baseline: users table and star-schema warehouse.

This migration creates the complete initial schema exactly as defined by the
ORM models, EXCEPT the refresh-token rotation columns on ``users`` — those are
added by revision ``002`` so that existing deployments upgrade cleanly.

Tables created:
    users
    dim_customer, dim_product, dim_region, dim_channel, dim_date
    fact_sales (references all five dimensions)

Revision ID: 001
Revises:
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the users table and the full star-schema warehouse."""
    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # Dimension tables
    # ------------------------------------------------------------------
    op.create_table(
        "dim_customer",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_code", sa.String(length=100), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dim_customer_customer_code",
        "dim_customer",
        ["customer_code"],
        unique=True,
    )

    op.create_table(
        "dim_product",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_code", sa.String(length=100), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dim_product_product_code",
        "dim_product",
        ["product_code"],
        unique=True,
    )

    op.create_table(
        "dim_region",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("region_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("region_name"),
    )

    op.create_table(
        "dim_channel",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel_name"),
    )

    op.create_table(
        "dim_date",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("full_date"),
    )

    # ------------------------------------------------------------------
    # Fact table
    # ------------------------------------------------------------------
    op.create_table(
        "fact_sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("region_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["dim_customer.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["dim_product.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["dim_region.id"]),
        sa.ForeignKeyConstraint(["channel_id"], ["dim_channel.id"]),
        sa.ForeignKeyConstraint(["date_id"], ["dim_date.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fact_sales_date", "fact_sales", ["date_id"])
    op.create_index("ix_fact_sales_customer", "fact_sales", ["customer_id"])


def downgrade() -> None:
    """Drop the entire baseline schema in reverse dependency order."""
    op.drop_index("ix_fact_sales_customer", table_name="fact_sales")
    op.drop_index("ix_fact_sales_date", table_name="fact_sales")
    op.drop_table("fact_sales")

    op.drop_table("dim_date")
    op.drop_table("dim_channel")
    op.drop_table("dim_region")

    op.drop_index("ix_dim_product_product_code", table_name="dim_product")
    op.drop_table("dim_product")

    op.drop_index("ix_dim_customer_customer_code", table_name="dim_customer")
    op.drop_table("dim_customer")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
