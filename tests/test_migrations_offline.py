"""Offline migration checks that need no database, Docker, or network.

Run as a script (`python tests/test_migrations_offline.py`) for a pre-push
gate, or via pytest alongside the live-database suite.
"""

from __future__ import annotations

import io
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Dummy settings so `app.config` imports when env.py runs; offline mode compiles
# DDL and never opens a connection, so the values are irrelevant.
os.environ.setdefault("POSTGRES_HOST", "offline")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "offline")
os.environ.setdefault("POSTGRES_USER", "offline")
os.environ.setdefault("POSTGRES_PASSWORD", "offline")
os.environ.setdefault("SECRET_KEY", "offline-check-secret-not-for-production")

from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command

_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_TABLES = {
    "users",
    "dim_customer",
    "dim_product",
    "dim_region",
    "dim_channel",
    "dim_date",
    "fact_sales",
    "conversation_turns",
}


def _alembic_config() -> Config:
    """Alembic config bound to the repo's alembic.ini and versions directory."""
    cfg = Config(str(_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_ROOT / "alembic"))
    return cfg


def _offline_upgrade_sql() -> str:
    """Return the DDL Alembic emits to build the schema from an empty database."""
    ddl = io.StringIO()
    # Alembic prints its runtime banner to stderr; drop it so the DDL is clean.
    with redirect_stdout(ddl), redirect_stderr(io.StringIO()):
        command.upgrade(_alembic_config(), "head", sql=True)
    return ddl.getvalue()


def _iter_app_sources():
    """Yield every Python source file under app/."""
    return (_ROOT / "app").rglob("*.py")


def test_single_head_and_linear_chain():
    """Revisions form one linear chain: base -> 001 -> 002 -> 003 (single head)."""
    script = ScriptDirectory.from_config(_alembic_config())

    assert list(script.get_heads()) == ["003"]
    assert script.get_revision("001").down_revision is None
    assert script.get_revision("002").down_revision == "001"
    assert script.get_revision("003").down_revision == "002"


def test_offline_upgrade_sql_emits_full_schema():
    """Offline `alembic upgrade head` emits DDL for every table without a DB."""
    sql = _offline_upgrade_sql().lower()

    for tbl in EXPECTED_TABLES:
        assert f"create table {tbl}" in sql, f"missing DDL for {tbl}"
    for col in ("refresh_token_jti", "refresh_token_hash"):
        assert col in sql, f"missing refresh-token column {col}"
    for idx in (
        "ix_users_email",
        "ix_fact_sales_date",
        "ix_users_refresh_token_jti",
        "ix_conversation_turns_session_id",
        "ix_conversation_turns_expires_at",
    ):
        assert idx in sql, f"missing index {idx}"


def test_no_runtime_create_all_in_app():
    """Application code never calls create_all (schema is Alembic-owned)."""
    offenders = [
        src.relative_to(_ROOT).as_posix()
        for src in _iter_app_sources()
        if "create_all" in src.read_text(encoding="utf-8")
    ]

    assert not offenders, f"create_all found in: {offenders}"


def main() -> int:
    """Run the offline checks as a script and report a pass/fail summary."""
    checks = (
        test_single_head_and_linear_chain,
        test_offline_upgrade_sql_emits_full_schema,
        test_no_runtime_create_all_in_app,
    )

    failed = 0
    for check in checks:
        try:
            check()
            print(f"PASS  {check.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {check.__name__}: {exc}")

    print(f"\n{len(checks) - failed}/{len(checks)} offline checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
