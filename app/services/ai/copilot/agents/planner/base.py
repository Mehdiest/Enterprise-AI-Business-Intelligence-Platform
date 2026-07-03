"""
Base planner interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.services.ai.copilot.context.models import (
    RetrievalContext,
)

from .models import ExecutionPlan


class BasePlanner(
    ABC,
):
    """
    Abstract planner.
    """

    @abstractmethod
    def build_plan(
        self,
        question: str,
        context: RetrievalContext | None = None,
    ) -> ExecutionPlan:
        ...