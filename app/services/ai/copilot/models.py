"""
Copilot domain models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """
    Represents a knowledge source used
    to generate an answer.
    """

    id: str

    text: str

    score: float


class RetrievedContext(BaseModel):
    """
    Represents retrieved semantic context.
    """

    documents: list[SourceReference] = Field(
        default_factory=list
    )


class CopilotRequest(BaseModel):
    """
    User request sent to AI Copilot.
    """

    question: str

    session_id: str | None = None


class CopilotResponse(BaseModel):
    """
    Final AI response.
    """

    answer: str

    confidence: float = 0.0

    session_id: str | None = None

    sources: list[
        SourceReference
    ] = Field(
        default_factory=list
    )
