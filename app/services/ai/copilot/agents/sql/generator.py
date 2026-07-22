"""Schema-aware SQL generation with an optional LLM backend."""

from __future__ import annotations

import inspect
import logging
import re

from app.services.ai.providers import ProviderFactory

from .models import SQLGenerationResult, SQLPlan
from .prompts import (
    SQL_SYSTEM_PROMPT,
    WAREHOUSE_SCHEMA,
)

logger = logging.getLogger(__name__)


class SQLGenerator:
    def __init__(self, provider=None) -> None:
        self.provider = provider or ProviderFactory.create()

    async def generate(self, question: str, plan: SQLPlan) -> SQLGenerationResult:
        generated = await self._generate_via_llm(question, plan)

        if generated and self._is_safe_select(generated):
            return SQLGenerationResult(sql=generated)

        return SQLGenerationResult(sql=self._fallback(question))

    async def _generate_via_llm(self, question: str, plan: SQLPlan) -> str:
        """Ask the LLM provider for SQL; return "" on any provider failure."""
        prompt = (
            f"{SQL_SYSTEM_PROMPT}\n\n"
            f"Warehouse schema:\n"
            f"{WAREHOUSE_SCHEMA}\n\n"
            f"Question: {question}\n"
            f"Plan: {plan.model_dump_json()}\n"
            "SQL:"
        )

        try:
            result = self.provider.generate(prompt)
            response = await result if inspect.isawaitable(result) else result
        except Exception:
            logger.exception("LLM SQL generation failed | question=%s", question)
            return ""

        return self._extract_sql(response)

    @staticmethod
    def _extract_sql(value: str | None) -> str:
        if not value:
            return ""
        match = re.search(
            r"```(?:sql)?\s*(.*?)```",
            value,
            re.IGNORECASE | re.DOTALL,
        )
        return (
            match.group(1)
            if match
            else value
        ).strip().rstrip(";")

    @staticmethod
    def _is_safe_select(sql: str) -> bool:
        return (
            bool(re.match(r"^\s*select\b", sql, re.IGNORECASE))
            and ";" not in sql
        )

    @staticmethod
    def _fallback(question: str) -> str:
        q = question.lower()
        if "top" in q and "product" in q:
            return (
                "SELECT p.product_name, SUM(f.amount) AS revenue "
                "FROM fact_sales AS f JOIN dim_product AS p ON f.product_id = p.id "
                "GROUP BY p.product_name ORDER BY revenue DESC LIMIT 1"
            )
        if "region" in q:
            return (
                "SELECT r.region_name, SUM(f.amount) AS revenue "
                "FROM fact_sales AS f JOIN dim_region AS r ON f.region_id = r.id "
                "GROUP BY r.region_name ORDER BY revenue DESC"
            )
        if "average" in q:
            return "SELECT AVG(amount) AS average_sales FROM fact_sales"
        if "total sales" in q or "revenue" in q:
            return "SELECT SUM(amount) AS total_sales FROM fact_sales"
        return (
            "SELECT id, customer_id, product_id, region_id, channel_id, "
            "date_id, quantity, amount FROM fact_sales LIMIT 10"
        )