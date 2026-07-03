"""
Conversation session.
"""

from __future__ import annotations

from uuid import uuid4


class ConversationSession:
    """
    Conversation session identifier.
    """

    def __init__(self) -> None:
        self.session_id = str(uuid4())

    def __str__(self) -> str:
        return self.session_id