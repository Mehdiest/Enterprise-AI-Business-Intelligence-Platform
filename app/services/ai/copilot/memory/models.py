"""
Conversation models.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class ConversationMessage(
    BaseModel,
):
    """
    Conversation message.
    """

    role: str

    content: str

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
    )