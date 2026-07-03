"""
Conversation context window.
"""

from __future__ import annotations

from .models import ConversationMessage


class ContextWindow:
    """
    Maintains a rolling conversation window.
    """

    def __init__(
        self,
        max_messages: int = 10,
    ) -> None:

        self.max_messages = max_messages

    def build(
        self,
        history: list[ConversationMessage],
    ) -> list[ConversationMessage]:

        if len(history) <= self.max_messages:
            return history

        return history[-self.max_messages :]