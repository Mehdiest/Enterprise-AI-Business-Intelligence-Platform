"""SQL executor backed by the application's async session factory."""

from __future__ import annotations

import logging
import time

from sqlalchemy import text

from app.database import SessionLocal

from .models import SQLExecutionResult

logger = logging.getLogger(__name__)


class SQLExecutor:
    """Execute validated read-only SQL."""

    async def execute(self, sql: str) -> SQLExecutionResult:
        """Run `sql` and return its rows with the elapsed execution time."""
        start = time.perf_counter()

        try:
            async with SessionLocal() as session:
                result = await session.execute(text(sql))
                rows = [dict(row._mapping) for row in result]

        except Exception:
            logger.exception("SQL execution failed | sql=%s", sql)
            raise

        return SQLExecutionResult(
            sql=sql,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=round(
                (time.perf_counter() - start) * 1000,
                2,
            ),
        )