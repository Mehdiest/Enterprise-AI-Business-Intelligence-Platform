"""
Enterprise AI Copilot Engine.

Coordinates the complete AI pipeline.
"""

from __future__ import annotations

from app.services.ai.copilot.context import (
    ContextBuilder,
)

from app.services.ai.copilot.intent import (
    RuleBasedIntentClassifier,
)

from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
    SourceReference,
)


class CopilotEngine:
    """
    Enterprise AI pipeline orchestrator.
    """

    def __init__(self):

        self.intent_classifier = (
            RuleBasedIntentClassifier()
        )

        self.context_builder = (
            ContextBuilder()
        )

    def process(
        self,
        request: CopilotRequest,
    ) -> CopilotResponse:

        intent = (
            self.intent_classifier.classify(
                request.question
            )
        )

        context = (
            self.context_builder.build(
                request.question
            )
        )

        answer = (
            f"Intent: {intent.intent.value}\n\n"
            f"Retrieved {len(context.documents)} "
            f"context documents."
        )

        return CopilotResponse(
            answer=answer,
            confidence=intent.confidence,
            sources=[
                SourceReference(
                    id=str(index + 1),
                    text=document.text,
                    score=document.score,
                )
                for index, document in enumerate(
                    context.documents
                )
            ],
        )