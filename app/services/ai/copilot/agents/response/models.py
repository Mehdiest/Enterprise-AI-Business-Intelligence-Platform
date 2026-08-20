"""Response domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResponseContext(BaseModel):
    """Final response context passed to the prompt builder."""

    question: str
    retrieved_context: list[str] = Field(default_factory=list)
    sql_result: dict | None = None
    analytics: dict | None = None
    citations: list[str] = Field(default_factory=list)
    confidence: float = 1.0
