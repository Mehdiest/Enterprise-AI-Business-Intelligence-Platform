"""
Planner routing rules.
"""

from __future__ import annotations

from .models import ExecutionStep


class PlannerRules:
    """
    Rule repository used by
    the planner agent.
    """

    @staticmethod
    def resolve(
        question: str,
    ) -> tuple[
        list[ExecutionStep],
        str,
    ]:

        q = question.lower()

        if any(
            word in q
            for word in (
                "chart",
                "plot",
                "graph",
                "visual",
            )
        ):

            return (
                [
                    ExecutionStep.RETRIEVE,
                    ExecutionStep.ANALYTICS,
                    ExecutionStep.CHART,
                    ExecutionStep.RESPONSE,
                ],
                "Chart request detected.",
            )

        if any(
            word in q
            for word in (
                "sales",
                "revenue",
                "product",
                "region",
                "best",
                "top",
            )
        ):

            return (
                [
                    ExecutionStep.RETRIEVE,
                    ExecutionStep.SQL,
                    ExecutionStep.ANALYTICS,
                    ExecutionStep.RESPONSE,
                ],
                "Business analytics request detected.",
            )

        return (
            [
                ExecutionStep.RETRIEVE,
                ExecutionStep.RESPONSE,
            ],
            "Default execution strategy.",
        )