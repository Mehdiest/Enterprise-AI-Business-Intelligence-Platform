"""
Enterprise Multi-Agent Copilot Engine.
"""

from __future__ import annotations

import inspect

from sqlalchemy.ext.asyncio import AsyncSession

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

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.intent = RuleBasedIntentClassifier()
        self.context_builder = ContextBuilder(db=db)
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
        runtime.metadata["session_id"] = session_id

        # ExecutionEngine handles sync and async agents transparently
        runtime = await self.executor.execute(runtime)

        answer = await self._build_answer(runtime, retrieval)

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

    async def _build_answer(
        self,
        runtime: ExecutionContext,
        retrieval,
    ) -> str:
        """Use the tool-calling answer when available, else query the LLM."""
        if runtime.metadata.get("tool_calling") and runtime.response:
            return runtime.response

        prompt = self.prompt_builder.build(
            question=runtime.question,
            context=retrieval,
            sql_result=getattr(runtime, "sql_result", {}),
        )

        answer = self.llm.generate(prompt)
        return await answer if inspect.isawaitable(answer) else answer
