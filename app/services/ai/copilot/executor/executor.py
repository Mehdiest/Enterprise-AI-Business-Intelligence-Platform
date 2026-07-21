"""Enterprise execution engine."""

from __future__ import annotations

import inspect

from app.services.ai.copilot.context_runtime import ExecutionContext
from app.services.ai.copilot.executor.base import BaseExecutor
from app.services.ai.copilot.executor.registry import AgentRegistry


class ExecutionEngine(BaseExecutor):
    """Executes an execution plan.

    Each step is resolved through the AgentRegistry. Handlers may be
    sync or async — the result is awaited only when it's a coroutine,
    so agents can be migrated to async independently of one another.
    """

    def __init__(self) -> None:
        self.registry = AgentRegistry()

    async def execute(self, context: ExecutionContext) -> ExecutionContext:
        """Run each planned step in order, awaiting async handlers."""
        if context.plan is None:
            return context

        for step in context.plan.steps:
            handler = self.registry.get(step)
            if handler is None:
                continue

            result = handler(context)
            context = await result if inspect.isawaitable(result) else result

        return context