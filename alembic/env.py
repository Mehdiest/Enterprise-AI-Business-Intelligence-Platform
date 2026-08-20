"""Alembic migration environment.

This env.py is async-aware because the application uses the asyncpg driver.
It resolves the database URL and the target metadata directly from the
application code, guaranteeing that migrations describe the exact same schema
the ORM defines.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Import application settings and metadata.
#
# Importing the model modules is required so that every table is registered on
# Base.metadata before autogenerate/compare runs.
# ---------------------------------------------------------------------------
from app.config import settings
from app.database import Base
from app.models import user as _user  # noqa: F401  (register User table)
from app.models import warehouse as _warehouse  # noqa: F401  (register warehouse tables)

# Alembic Config object, providing access to values in alembic.ini.
config = context.config

# Inject the runtime database URL from application settings so we never commit
# credentials to alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configure Python logging from the alembic.ini file, if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to stdout, no DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure the context with a live connection and run the migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations within an async connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live async database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
