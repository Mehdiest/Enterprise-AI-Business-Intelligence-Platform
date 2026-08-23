"""Programmatic Alembic helpers for the test suite.

These helpers let tests build and tear down the schema *exclusively* through
Alembic migrations — the same path production uses — instead of
``Base.metadata.create_all``. This guarantees that the committed migrations
actually reproduce the ORM schema, which is the Phase 1 exit condition.
"""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command

# Repository root (…/tests/_migrations.py -> repo root is two levels up).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ALEMBIC_INI = _PROJECT_ROOT / "alembic.ini"


def make_alembic_config(database_url: str) -> Config:
    """Return an Alembic ``Config`` bound to ``database_url``.

    The URL is injected at runtime so tests can target their own throwaway
    database without touching committed configuration.
    """
    config = Config(str(_ALEMBIC_INI))
    config.set_main_option("script_location", str(_PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def upgrade_to_head(database_url: str) -> None:
    """Apply every migration up to ``head`` against ``database_url``."""
    command.upgrade(make_alembic_config(database_url), "head")


def downgrade_to_base(database_url: str) -> None:
    """Revert every migration down to ``base`` (empty schema)."""
    command.downgrade(make_alembic_config(database_url), "base")
