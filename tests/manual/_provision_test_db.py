"""One-off helper: provision the `test` role and `test_db` database locally.

Tries a list of common superuser credentials until one connects, then creates
the throwaway test role/database the suite expects. Safe to re-run.

Usage:
    python tests/manual/_provision_test_db.py
"""

from __future__ import annotations

import asyncio

import asyncpg

CANDIDATE_SUPERUSERS = [
    ("postgres", "postgres"),
    ("postgres", ""),
    ("postgres", "admin"),
    ("postgres", "root"),
    ("postgres", "password"),
    ("postgres", "1234"),
    ("postgres", "postgres123"),
]

TEST_USER = "test"
TEST_PASSWORD = "test"
TEST_DB = "test_db"


async def _try_connect(user: str, password: str):
    try:
        return await asyncpg.connect(
            host="localhost",
            port=5432,
            user=user,
            password=password,
            database="postgres",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  - {user}/{password!r}: {type(exc).__name__}")
        return None


async def main() -> int:
    conn = None
    for user, password in CANDIDATE_SUPERUSERS:
        conn = await _try_connect(user, password)
        if conn is not None:
            print(f"Connected as superuser {user!r}.")
            break

    if conn is None:
        print(
            "\nCould not connect with any candidate superuser credential.\n"
            "Please create the test role/db manually, e.g.:\n"
            "  CREATE ROLE test LOGIN PASSWORD 'test';\n"
            "  CREATE DATABASE test_db OWNER test;\n"
        )
        return 1

    try:
        role_exists = await conn.fetchval(
            "SELECT 1 FROM pg_roles WHERE rolname = $1", TEST_USER
        )
        if not role_exists:
            await conn.execute(
                f"CREATE ROLE {TEST_USER} LOGIN PASSWORD '{TEST_PASSWORD}'"
            )
            print(f"Created role {TEST_USER!r}.")
        else:
            print(f"Role {TEST_USER!r} already exists.")

        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB
        )
        if not db_exists:
            await conn.execute(f"CREATE DATABASE {TEST_DB} OWNER {TEST_USER}")
            print(f"Created database {TEST_DB!r}.")
        else:
            print(f"Database {TEST_DB!r} already exists.")

        # Ensure the test role can create/drop schema objects.
        await conn.execute(
            f"GRANT ALL PRIVILEGES ON DATABASE {TEST_DB} TO {TEST_USER}"
        )
    finally:
        await conn.close()

    # Grant schema-level privileges inside the test database itself.
    admin_db_conn = None
    for user, password in CANDIDATE_SUPERUSERS:
        try:
            admin_db_conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user=user,
                password=password,
                database=TEST_DB,
            )
            break
        except Exception:  # noqa: BLE001
            continue

    if admin_db_conn is not None:
        try:
            await admin_db_conn.execute(
                f"GRANT ALL ON SCHEMA public TO {TEST_USER}"
            )
            await admin_db_conn.execute(
                f"ALTER SCHEMA public OWNER TO {TEST_USER}"
            )
            print("Granted schema privileges to test role.")
        finally:
            await admin_db_conn.close()

    print("\nProvisioning complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
