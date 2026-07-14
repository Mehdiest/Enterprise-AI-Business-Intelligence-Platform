"""Builds LLM prompts from question, context and query results."""

from __future__ import annotations

from app.services.ai.copilot.context.models import (
    RetrievalContext,
)

from .templates import SYSTEM_PROMPT


class PromptBuilder:
    """Builds prompts for LLMs."""

    def build(
        self,
        question: str,
        context: RetrievalContext,
        sql_result: dict | None = None,
    ) -> str:
        """Compose the full prompt; includes query rows when available."""

        context_text = "\n".join(
            f"- {doc.text}"
            for doc in context.documents
        )

        data_section = self._format_data(sql_result)

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Question:\n{question}\n\n"
            f"Context:\n{context_text}\n\n"
            f"{data_section}"
            f"Answer:"
        )

    @staticmethod
    def _format_data(sql_result: dict | None) -> str:
        """Render up to 10 result rows as a Data block, else empty."""

        rows = (sql_result or {}).get("rows") or []

        if not rows:
            return ""

        lines = [
            ", ".join(f"{key}={value}" for key, value in row.items())
            for row in rows[:10]
        ]

        return "Data:\n" + "\n".join(f"- {line}" for line in lines) + "\n\n"
