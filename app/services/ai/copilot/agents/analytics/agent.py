"""Analytics agent that summarizes retrieved documents."""

from __future__ import annotations

from app.services.ai.copilot.context_runtime import ExecutionContext

from .base import BaseAnalyticsAgent


class AnalyticsAgent(BaseAnalyticsAgent):
    """Extract business analytics from retrieved semantic context."""

    def run(self, context: ExecutionContext) -> ExecutionContext:
        documents = (
            context.retrieved_context.documents
            if context.retrieved_context
            else []
        )

        context.analytics = {
            "document_count": len(documents),
            "highest_score": max(
                (doc.score for doc in documents),
                default=0.0,
            ),
            "top_document": documents[0].text if documents else None,
        }

        return context
