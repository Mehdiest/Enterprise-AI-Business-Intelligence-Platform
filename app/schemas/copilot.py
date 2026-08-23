"""
Copilot API schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    """
    Copilot request.
    """

    question: str = Field(
        ...,
        min_length=1,
    )

    session_id: str | None = None


class SourceItem(BaseModel):

    id: str

    text: str

    score: float


class CopilotResponse(BaseModel):
    """
    Copilot response.
    """

    answer: str

    confidence: float

    session_id: str | None = None

    sources: list[SourceItem] = []
