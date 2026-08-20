"""SQL agent domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SQLPlan(BaseModel):
    """SQL execution strategy for a question."""

    requires_sql: bool
    target_table: str | None = None
    operation: str
    explanation: str


class SQLGenerationResult(BaseModel):
    """Generated SQL query."""

    sql: str
    parameters: list = Field(default_factory=list)


class SQLExecutionResult(BaseModel):
    """SQL execution output."""

    sql: str
    rows: list[dict] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
