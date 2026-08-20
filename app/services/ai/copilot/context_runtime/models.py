"""
Runtime execution context models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.services.ai.copilot.agents.planner.models import (
    ExecutionPlan,
)
from app.services.ai.copilot.context.models import (
    RetrievalContext,
)
from app.services.ai.copilot.intent.models import (
    IntentResult,
)


class ExecutionContext(BaseModel):
    """
    Shared runtime context.

    Every enterprise agent receives
    the same runtime object.
    """

    question: str

    intent: IntentResult | None = None

    plan: ExecutionPlan | None = None

    retrieved_context: RetrievalContext | None = None

    analytics: dict = Field(
        default_factory=dict,
    )

    sql_result: dict = Field(
        default_factory=dict,
    )

    chart: dict = Field(
        default_factory=dict,
    )

    response: str = ""

    metadata: dict = Field(
        default_factory=dict,
    )