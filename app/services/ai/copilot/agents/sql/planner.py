"""SQL planner that decides whether a question requires warehouse SQL."""

from __future__ import annotations

from .models import SQLPlan

_SQL_KEYWORDS = (
    "sales",
    "revenue",
    "product",
    "customer",
    "order",
    "region",
    "month",
    "year",
    "top",
    "average",
    "sum",
    "count",
    "total",
)


class SQLPlanner:
    """Determine whether a question requires SQL execution."""

    def build_plan(self, question: str) -> SQLPlan:
        """Create a SQL execution plan from user intent."""
        normalized = question.lower()
        requires_sql = any(keyword in normalized for keyword in _SQL_KEYWORDS)

        return SQLPlan(
            requires_sql=requires_sql,
            target_table="fact_sales" if requires_sql else None,
            operation="analytics" if requires_sql else "none",
            explanation=(
                "Business analytics query requiring warehouse SQL."
                if requires_sql
                else "No SQL execution required."
            ),
        )
