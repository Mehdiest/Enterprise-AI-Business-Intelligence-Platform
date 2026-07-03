"""
Context models.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class ContextDocument(BaseModel):
    """
    Retrieved context document.
    """

    text: str

    score: float


class RetrievalContext(BaseModel):
    """
    Semantic retrieval context.
    """

    documents: list[
        ContextDocument
    ] = Field(
        default_factory=list
    )

    conversation: list[
        str
    ] = Field(
        default_factory=list
    )