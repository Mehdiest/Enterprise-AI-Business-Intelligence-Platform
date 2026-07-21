"""
Enterprise Multi-Agent Copilot Engine.
"""

from __future__ import annotations

import inspect

from app.services.ai.copilot.agents.planner import PlannerAgent
from app.services.ai.copilot.context import ContextBuilder
from app.services.ai.copilot.context_runtime import ExecutionContext
from app.services.ai.copilot.executor import ExecutionEngine
from app.services.ai.copilot.intent import RuleBasedIntentClassifier
from app.services.ai.copilot.models import (
    CopilotRequest,
    CopilotResponse,
    SourceReference,
)
from app.services.ai.copilot.prompt import PromptBuilder
from app.services.ai.providers import ProviderFactory


class CopilotEngine:
    """
    Enterprise Multi-Agent Engine.

    Pipeline

    Request
        ↓
    Intent
        ↓
    Context Builder
        ↓
    Planner
        ↓
    Executor
        ↓
    Prompt Builder
        ↓
    LLM
        ↓
    Response
    """

    def __init__(self) -> None:
        self.intent = RuleBasedIntentClassifier()
        self.context_builder = ContextBuilder()
        self.planner = PlannerAgent()
        self.executor = ExecutionEngine()
        self.prompt_builder = PromptBuilder()
        self.llm = ProviderFactory.create()

    async def process(
        self,
        request: CopilotRequest,
        session_id: str | None = None,
    ) -> CopilotResponse:
        """
        Execute the complete Copilot pipeline.
        """

        intent = self.intent.classify(request.question)

        retrieval = await self.context_builder.build(
            question=request.question,
            session_id=session_id,
        )

        plan = self.planner.build_plan(
            request.question,
            retrieval,
        )

        runtime = ExecutionContext(
            question=request.question,
        )

        runtime.plan = plan
        runtime.retrieved_context = retrieval

        # ExecutionEngine handles sync and async agents transparently
        runtime = await self.executor.execute(runtime)

        prompt = self.prompt_builder.build(
            question=runtime.question,
            context=retrieval,
            sql_result=getattr(runtime, "sql_result", {}),
        )

        # Providers may be sync or async depending on backend
        answer = self.llm.generate(prompt)
        if inspect.isawaitable(answer):
            answer = await answer

        sources = [
            SourceReference(
                id=str(index),
                text=citation,
                score=1.0,
            )
            for index, citation in enumerate(
                runtime.citations,
                start=1,
            )
        ]

        return CopilotResponse(
            answer=answer,
            confidence=intent.confidence,
            sources=sources,
        )
