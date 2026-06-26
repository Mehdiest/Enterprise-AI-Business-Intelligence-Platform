"""
Prompt builder.
"""

from __future__ import annotations

from app.services.ai.copilot.context.models import (
    RetrievalContext,
)

from .templates import SYSTEM_PROMPT


class PromptBuilder:
    """
    Builds prompts for LLMs.
    """

    def build(
        self,
        question: str,
        context: RetrievalContext,
    ) -> str:

        context_text = "\n".join(
            f"- {doc.text}"
            for doc in context.documents
        )

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Question:\n"
            f"{question}\n\n"
            f"Context:\n"
            f"{context_text}\n\n"
            f"Answer:"
        )