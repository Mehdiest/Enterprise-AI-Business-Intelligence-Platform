"""Planner routing rules."""

from __future__ import annotations

from .models import ExecutionStep

_CHART_WORDS = ("chart", "plot", "graph", "visual")
_ANALYTICS_WORDS = ("sales", "revenue", "product", "region", "best", "top")


class PlannerRules:
    """Resolve a question to an ordered set of execution steps."""

    @staticmethod
    def resolve(question: str) -> tuple[list[ExecutionStep], str]:
        q = question.lower()

        if any(word in q for word in _CHART_WORDS):
            return (
                [
                    ExecutionStep.RETRIEVE,
                    ExecutionStep.ANALYTICS,
                    ExecutionStep.CHART,
                    ExecutionStep.RESPONSE,
                ],
                "Chart request detected.",
            )

        if any(word in q for word in _ANALYTICS_WORDS):
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
            [ExecutionStep.RETRIEVE, ExecutionStep.RESPONSE],
            "Default execution strategy.",
        )
