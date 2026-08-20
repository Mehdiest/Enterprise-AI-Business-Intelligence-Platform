#!/usr/bin/env sh
# ============================================================================
# Container entrypoint: MIGRATE, THEN SERVE.
#
# The application no longer creates tables at runtime (create_all was removed),
# so the schema MUST be applied by Alembic before the API starts accepting
# traffic. This script makes that ordering deterministic on every deploy:
#
#     1. alembic upgrade head   (bring the DB schema to the latest revision)
#     2. exec uvicorn ...       (serve the API as PID 1 for clean signals)
#
# `exec` replaces the shell so SIGTERM/SIGINT reach uvicorn directly, giving
# graceful shutdown in Docker/Kubernetes.
# ============================================================================
set -e

echo "[entrypoint] Applying database migrations (alembic upgrade head)..."
alembic upgrade head
echo "[entrypoint] Migrations complete."

echo "[entrypoint] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
