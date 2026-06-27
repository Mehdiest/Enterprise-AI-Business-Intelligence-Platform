"""
Enterprise AI Copilot engine.
"""

from __future__ import annotations

from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
    SourceReference,
)

from app.services.ai.copilot.intent import (
    RuleBasedIntentClassifier,
)

from app.services.ai.copilot.context import (
    ContextBuilder,
)

from app.services.ai.copilot.prompt import (
    PromptBuilder,
)

from app.services.ai.llm import (
    LLMFactory,
)


class CopilotEngine:
    """
    Enterprise AI Copilot orchestration pipeline.
    """

    def __init__(self):

        self.intent = (
            RuleBasedIntentClassifier()
        )

        self.context = (
            ContextBuilder()
        )

        self.prompt_builder = (
            PromptBuilder()
        )

        self.llm = (
            LLMFactory.create()
        )

    def process(
        self,
        request: CopilotRequest,
    ) -> CopilotResponse:

        intent = (
            self.intent.classify(
                request.question
            )
        )

        context = (
            self.context.build(
                request.question
            )
        )

        prompt = (
            self.prompt_builder.build(
                question=request.question,
                context=context,
            )
        )

        answer = (
            self.llm.generate(
                prompt
            )
        )

        sources = []

        for index, document in enumerate(
            context.documents,
            start=1,
        ):

            sources.append(
                SourceReference(
                    id=str(index),
                    text=document.text,
                    score=document.score,
                )
            )

        return CopilotResponse(
            answer=answer,
            confidence=intent.confidence,
            sources=sources,
        )