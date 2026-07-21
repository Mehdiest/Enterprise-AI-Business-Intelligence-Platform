"""
Enterprise SQL planner.
"""

from __future__ import annotations

from .models import SQLPlan


class SQLPlanner:
    """
    Determine whether a question requires SQL execution.
    """

    SQL_KEYWORDS = (
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

    def build_plan(
        self,
        question: str,
    ) -> SQLPlan:
        """
        Create SQL execution plan from user intent.
        """

        normalized_question = question.lower()

        requires_sql = any(
            keyword in normalized_question
            for keyword in self.SQL_KEYWORDS
        )

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