"""Read-only SQL query tool backed by the warehouse executor."""

from __future__ import annotations

import logging
from typing import Any

from app.services.ai.copilot.agents.sql.executor import SQLExecutor
from app.services.ai.copilot.agents.sql.validator import SQLValidator

from .base import BaseTool
from .models import (
    ToolCallResult,
    ToolContext,
    ToolDefinition,
    ToolParameter,
    ToolParameterType,
)

logger = logging.getLogger(__name__)

MAX_ROWS_RETURNED = 50


class SQLQueryTool(BaseTool):
    """Execute a validated SELECT against the star-schema warehouse."""

    def __init__(self) -> None:
        self.validator = SQLValidator()
        self.executor = SQLExecutor()

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="run_sql_query",
            description=(
                "Execute a read-only SELECT query against the BI warehouse. "
                "Star schema: fact_sales joined to dim_product, dim_region, "
                "dim_customer, dim_channel, dim_date. Only SELECT is allowed."
            ),
            parameters=[
                ToolParameter(
                    name="sql",
                    type=ToolParameterType.STRING,
                    description=(
                        "A single SELECT statement. Example: SELECT p.product_name, "
                        "SUM(f.amount) AS revenue FROM fact_sales f JOIN dim_product p "
                        "ON f.product_id = p.id GROUP BY p.product_name "
                        "ORDER BY revenue DESC LIMIT 5"
                    ),
                ),
            ],
        )

    async def execute(
        self, arguments: dict[str, Any], context: ToolContext
    ) -> ToolCallResult:
        sql = (arguments.get("sql") or "").strip()

        if not sql:
            return self._failure("No SQL query provided.")

        try:
            self.validator.validate(sql)
        except ValueError as exc:
            logger.warning("SQL tool rejected query | sql=%s | reason=%s", sql, exc)
            return self._failure(f"Query rejected: {exc}")

        try:
            execution = await self.executor.execute(sql)
        except Exception as exc:  # noqa: BLE001 - surface DB errors to the LLM
            logger.exception("SQL tool execution failed | sql=%s", sql)
            return self._failure(f"Query execution failed: {exc}")

        return ToolCallResult(
            tool_name=self.definition.name,
            success=True,
            output=self._build_output(execution),
        )

    def _failure(self, error: str) -> ToolCallResult:
        return ToolCallResult(
            tool_name=self.definition.name, success=False, error=error
        )

    @staticmethod
    def _build_output(execution) -> dict[str, Any]:
        rows = execution.rows[:MAX_ROWS_RETURNED]
        output: dict[str, Any] = {
            "sql": execution.sql,
            "rows": rows,
            "row_count": execution.row_count,
            "execution_time_ms": execution.execution_time_ms,
        }
        if execution.row_count > MAX_ROWS_RETURNED:
            output["note"] = (
                f"Showing first {MAX_ROWS_RETURNED} of {execution.row_count} rows."
            )
        return output