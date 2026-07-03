"""
Enterprise planner agent.
"""

from __future__ import annotations

from app.services.ai.copilot.context.models import (
    RetrievalContext,
)

from .base import BasePlanner
from .models import ExecutionPlan
from .rules import PlannerRules


class PlannerAgent(
    BasePlanner,
):
    """
    Enterprise planner.
    """

    def build_plan(
        self,
        question: str,
        context: RetrievalContext | None = None,
    ) -> ExecutionPlan:

        steps, reason = (
            PlannerRules.resolve(
                question
            )
        )

        conversation = []

        if context is not None:

            conversation = (
                context.conversation
            )

        return ExecutionPlan(
            steps=steps,
            reasoning=reason,
            conversation=conversation,
        )