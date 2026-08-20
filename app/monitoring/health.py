"""Check application and database health."""

from __future__ import annotations

import logging

from sqlalchemy import text

from app.database import engine

from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


class HealthChecker:
    """Run asynchronous service health probes."""

    @staticmethod
    async def database() -> bool:
        """Return whether the database accepts a probe query."""
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception:
            logger.exception("Database health probe failed")
            return False
        return True

    @classmethod
    async def status(cls) -> dict:
        """Return health status and process metrics."""
        database_ok = await cls.database()
        return {
            "status": "healthy" if database_ok else "unhealthy",
            "database": database_ok,
            "metrics": MetricsCollector.collect(),
        }