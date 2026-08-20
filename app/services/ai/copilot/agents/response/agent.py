"""Response agent that unifies execution outputs into one result."""

from __future__ import annotations

from app.services.ai.copilot.context_runtime import ExecutionContext

from .base import BaseResponseAgent
from .models import ResponseContext


class ResponseAgent(BaseResponseAgent):
    """Collect execution results into a unified response object."""

    async def run(self, context: ExecutionContext) -> ResponseContext:
        """Build the response context from retrieved documents and outputs."""
        retrieved = []
        citations = []

        if context.retrieved_context is not None:
            for document in context.retrieved_context.documents:
                retrieved.append(document.text)
                citations.append(document.text)

        return ResponseContext(
            question=context.question,
            retrieved_context=retrieved,
            sql_result=context.sql_result,
            analytics=context.analytics,
            citations=citations,
            confidence=1.0,
        )
