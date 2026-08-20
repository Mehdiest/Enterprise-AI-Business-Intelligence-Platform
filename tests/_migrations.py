"""Helpers for programmatically running Alembic migrations in tests."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def make_alembic_config(database_url: str) -> Config:
    """Create an Alembic Config pointing at the test database."""
    root_dir = Path(__file__).resolve().parent.parent
    config = Config(str(root_dir / "alembic.ini"))
    config.set_main_option("script_location", str(root_dir / "alembic"))
    
    # Alembic uses sync connections, so we strip the asyncpg driver
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    config.set_main_option("sqlalchemy.url", sync_url)
    
    return config


def upgrade_to_head(database_url: str) -> None:
    """Run `alembic upgrade head` against the given URL."""
    config = make_alembic_config(database_url)
    command.upgrade(config, "head")


def downgrade_to_base(database_url: str) -> None:
    """Run `alembic downgrade base` against the given URL."""
    config = make_alembic_config(database_url)
    command.downgrade(config, "base")