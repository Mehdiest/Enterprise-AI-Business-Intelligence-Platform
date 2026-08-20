"""Retriever agent that fetches semantic business context."""

from __future__ import annotations

from app.services.ai.copilot.context import ContextBuilder
from app.services.ai.copilot.context_runtime import ExecutionContext

from .base import BaseRetrieverAgent


class RetrieverAgent(BaseRetrieverAgent):
    """Retrieve semantic business context for a question."""

    def __init__(self):
        self.builder = ContextBuilder()

    async def run(self, context: ExecutionContext) -> ExecutionContext:
        context.retrieved_context = await self.builder.build(context.question)
        return context
