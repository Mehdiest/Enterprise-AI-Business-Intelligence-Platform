"""
Enterprise execution engine.
"""

from __future__ import annotations

from app.services.ai.copilot.context_runtime import (
    ExecutionContext,
)

from app.services.ai.copilot.executor.base import (
    BaseExecutor,
)

from app.services.ai.copilot.executor.registry import (
    AgentRegistry,
)


class ExecutionEngine(
    BaseExecutor,
):
    """
    Executes an execution plan.

    Each execution step is resolved
    through the AgentRegistry.
    """

    def __init__(
        self,
    ) -> None:

        self.registry = (
            AgentRegistry()
        )

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionContext:
        """
        Execute the current execution plan.
        """

        if context.plan is None:

            return context

        for step in context.plan.steps:

            handler = (
                self.registry.get(
                    step
                )
            )

            if handler is None:

                continue

            context = handler(
                context
            )

        return context