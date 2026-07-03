"""
Planner domain models.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class ExecutionStep(str, Enum):
    """
    Supported execution steps.
    """

    RETRIEVE = "retrieve"

    ANALYTICS = "analytics"

    SQL = "sql"

    CHART = "chart"

    RESPONSE = "response"


class ExecutionPlan(BaseModel):
    """
    Ordered execution plan.
    """

    steps: list[
        ExecutionStep
    ] = Field(
        default_factory=list
    )

    reasoning: str = ""

    conversation: list[
        str
    ] = Field(
        default_factory=list
    )