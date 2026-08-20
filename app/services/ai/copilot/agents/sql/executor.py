"""SQL executor backed by the application's async session factory."""

from __future__ import annotations

import logging
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import SessionLocal

from .models import SQLExecutionResult

logger = logging.getLogger(__name__)


class SQLExecutor:
    """Execute validated SQL inside a read-only, time-bounded transaction."""

    async def execute(self, sql: str) -> SQLExecutionResult:
        """Run `sql` under DB-level read-only and timeout guards; return its rows."""
        start = time.perf_counter()

        try:
            async with SessionLocal() as session, session.begin():
                await self._apply_guards(session)
                cursor = await session.execute(text(sql))
                rows = [dict(row._mapping) for row in cursor]

        except Exception:
            logger.exception("SQL execution failed | sql=%s", sql)
            raise

        return SQLExecutionResult(
            sql=sql,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=round((time.perf_counter() - start) * 1000, 2),
        )

    @staticmethod
    async def _apply_guards(session: AsyncSession) -> None:
        """Enforce read-only access and a statement timeout for this transaction."""
        timeout_ms = settings.sql_statement_timeout_ms
        await session.execute(text("SET TRANSACTION READ ONLY"))
        await session.execute(text(f"SET LOCAL statement_timeout = {timeout_ms}"))
