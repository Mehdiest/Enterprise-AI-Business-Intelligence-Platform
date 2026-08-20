"""Migration tests — the Phase 1 "deterministic deployment" gate.

These tests prove that:

1. A completely empty PostgreSQL database becomes the full application schema
   *only* through ``alembic upgrade head`` (no ``create_all``).
2. Every table the ORM defines exists after the upgrade, and the
   refresh-token columns added by revision ``002`` are present.
3. ``alembic downgrade base`` cleanly removes the entire schema.
4. The committed migrations do not drift from the ORM models — running
   Alembic's autogenerate against the migrated database produces no
   pending create/drop operations.

They run against the same throwaway PostgreSQL database the rest of the suite
uses (configured via POSTGRES_* env / .env.test).
"""

from __future__ import annotations

import asyncio

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from app.database import Base

# Import models so every table is registered on Base.metadata before we compare.
from app.models import user as _user  # noqa: F401
from app.models import warehouse as _warehouse  # noqa: F401
from tests._migrations import (
    downgrade_to_base,
    make_alembic_config,
    upgrade_to_head,
)
from tests.conftest import _build_db_url, _reset_schema

EXPECTED_TABLES = {
    "users",
    "dim_customer",
    "dim_product",
    "dim_region",
    "dim_channel",
    "dim_date",
    "fact_sales",
}


@pytest.fixture
def clean_database_url():
    """Yield a URL pointing at a freshly emptied database (no schema at all)."""
    database_url = _build_db_url()
    engine = create_async_engine(database_url)

    asyncio.run(_reset_schema(engine))
    asyncio.run(engine.dispose())

    yield database_url

    # Leave the database empty for the next test.
    engine = create_async_engine(database_url)
    asyncio.run(_reset_schema(engine))
    asyncio.run(engine.dispose())


def _table_names(database_url: str) -> set[str]:
    """Return the set of table names currently present in the database."""

    async def _inspect() -> set[str]:
        engine = create_async_engine(database_url)
        try:
            async with engine.connect() as connection:
                names = await connection.run_sync(
                    lambda sync_conn: set(inspect(sync_conn).get_table_names())
                )
            return names
        finally:
            await engine.dispose()

    return asyncio.run(_inspect())


def test_empty_database_upgrades_to_full_schema(clean_database_url):
    """An empty DB gains the full application schema via `alembic upgrade head`."""
    # Precondition: the database is empty (no application tables).
    before = _table_names(clean_database_url)
    assert EXPECTED_TABLES.isdisjoint(before), (
        f"Expected an empty database, but found application tables: "
        f"{EXPECTED_TABLES & before}"
    )

    # Act: build the schema exclusively through migrations.
    upgrade_to_head(clean_database_url)

    # Assert: every expected table now exists, plus Alembic's version table.
    after = _table_names(clean_database_url)
    missing = EXPECTED_TABLES - after
    assert not missing, f"Migrations did not create these tables: {missing}"
    assert "alembic_version" in after


def test_refresh_token_columns_present_after_upgrade(clean_database_url):
    """Revision 002's refresh-token columns exist after upgrading to head."""
    upgrade_to_head(clean_database_url)

    async def _columns() -> set[str]:
        engine = create_async_engine(clean_database_url)
        try:
            async with engine.connect() as connection:
                cols = await connection.run_sync(
                    lambda c: {col["name"] for col in inspect(c).get_columns("users")}
                )
            return cols
        finally:
            await engine.dispose()

    columns = asyncio.run(_columns())
    assert "refresh_token_jti" in columns
    assert "refresh_token_hash" in columns


def test_downgrade_to_base_removes_all_tables(clean_database_url):
    """`alembic downgrade base` fully tears the schema back down to empty."""
    upgrade_to_head(clean_database_url)
    assert EXPECTED_TABLES <= _table_names(clean_database_url)

    downgrade_to_base(clean_database_url)

    remaining = _table_names(clean_database_url)
    leftover = EXPECTED_TABLES & remaining
    assert not leftover, f"Downgrade left tables behind: {leftover}"


def test_migrations_match_orm_models_no_drift(clean_database_url):
    """Autogenerate against the migrated DB must yield NO pending changes.

    This is the anti-drift guard: if someone edits an ORM model without adding
    a migration (or vice-versa), Alembic will detect create/drop/alter
    operations here and this test fails.
    """
    upgrade_to_head(clean_database_url)

    def _diff(sync_connection) -> list:
        context = MigrationContext.configure(
            sync_connection,
            opts={"compare_type": True, "compare_server_default": True},
        )
        return compare_metadata(context, Base.metadata)

    async def _run_diff() -> list:
        engine = create_async_engine(clean_database_url)
        try:
            async with engine.connect() as connection:
                return await connection.run_sync(_diff)
        finally:
            await engine.dispose()

    diff = asyncio.run(_run_diff())

    # Ignore the internal alembic_version table if it ever shows up in the diff.
    meaningful = [
        change
        for change in diff
        if not (isinstance(change, tuple) and "alembic_version" in repr(change))
    ]
    assert not meaningful, (
        "ORM models and migrations have drifted. Pending operations detected:\n"
        + "\n".join(repr(change) for change in meaningful)
    )


def test_stamped_version_is_head(clean_database_url):
    """After upgrade, the recorded DB revision should be the latest (002)."""
    upgrade_to_head(clean_database_url)

    async def _version() -> str | None:
        engine = create_async_engine(clean_database_url)
        try:
            async with engine.connect() as connection:
                result = await connection.execute(
                    text("SELECT version_num FROM alembic_version")
                )
                row = result.first()
                return row[0] if row else None
        finally:
            await engine.dispose()

    assert asyncio.run(_version()) == "002"


def test_upgrade_is_reentrant_when_already_at_head(clean_database_url):
    """Running `upgrade head` twice is a no-op the second time (idempotent)."""
    upgrade_to_head(clean_database_url)
    first = _table_names(clean_database_url)

    # Second upgrade should not raise and should not change the schema.
    command.upgrade(make_alembic_config(clean_database_url), "head")
    second = _table_names(clean_database_url)

    assert first == second
