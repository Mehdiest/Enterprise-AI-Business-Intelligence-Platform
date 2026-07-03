"""
Conversation memory implementation.
"""

from __future__ import annotations

from .base import BaseMemory
from .models import ConversationMessage


class ConversationMemory(BaseMemory):
    """
    In-memory conversation storage.
    """

    def __init__(self) -> None:
        self._messages: list[ConversationMessage] = []

    def add(
        self,
        message: ConversationMessage,
    ) -> None:
        self._messages.append(message)

    def history(
        self,
    ) -> list[ConversationMessage]:
        return list(self._messages)

    def clear(
        self,
    ) -> None:
        self._messages.clear()