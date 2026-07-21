"""
Agent registry.
"""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable

from app.services.ai.copilot.agents.analytics import (
    AnalyticsAgent,
)
from app.services.ai.copilot.agents.planner.models import (
    ExecutionStep,
)
from app.services.ai.copilot.agents.response import (
    ResponseAgent,
)
from app.services.ai.copilot.agents.retriever import (
    RetrieverAgent,
)
from app.services.ai.copilot.agents.sql import (
    SQLAgent,
)
from app.services.ai.copilot.context_runtime import (
    ExecutionContext,
)


Handler = Callable[
    [ExecutionContext],
    Awaitable[ExecutionContext],
]


class AgentRegistry:
    """
    Registry for executable agents.
    """

    def __init__(self) -> None:

        retriever = RetrieverAgent()
        analytics = AnalyticsAgent()
        sql = SQLAgent()
        response = ResponseAgent()

        self._agents: dict[
            ExecutionStep,
            Handler,
        ] = {
            ExecutionStep.RETRIEVE: retriever.run,
            ExecutionStep.ANALYTICS: analytics.run,
            ExecutionStep.SQL: sql.run,
            ExecutionStep.RESPONSE: response.run,
        }

    def register(
        self,
        step: ExecutionStep,
        handler: Handler,
    ) -> None:
        """
        Register a new execution handler.
        """

        self._agents[step] = handler

    def unregister(
        self,
        step: ExecutionStep,
    ) -> None:
        """
        Remove a registered handler.
        """

        self._agents.pop(step, None)

    def exists(
        self,
        step: ExecutionStep,
    ) -> bool:
        """
        Check whether a handler exists.
        """

        return step in self._agents

    def get(
        self,
        step: ExecutionStep,
    ) -> Handler | None:
        """
        Return handler for a step.
        """

        return self._agents.get(step)

    def available_steps(
        self,
    ) -> list[ExecutionStep]:
        """
        Return all registered steps.
        """

        return list(self._agents.keys())