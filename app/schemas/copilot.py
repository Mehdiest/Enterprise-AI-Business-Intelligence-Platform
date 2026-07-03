"""
Copilot API schemas.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class CopilotRequest(BaseModel):
    """
    Copilot request.
    """

    question: str = Field(
        ...,
        min_length=1,
    )


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

    sources: list[SourceItem] = []