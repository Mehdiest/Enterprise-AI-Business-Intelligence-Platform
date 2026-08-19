"""Check application and database health."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


class HealthChecker:
    """Run asynchronous service health probes."""

    @staticmethod
    async def database() -> bool:
        """Return whether the database accepts a probe query."""
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
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