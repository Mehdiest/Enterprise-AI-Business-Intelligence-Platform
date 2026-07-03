"""
Conversation repository.
"""

from __future__ import annotations

from .memory import ConversationMemory


class MemoryRepository:
    """
    Memory repository.
    """

    def __init__(self) -> None:
        self.memory = ConversationMemory()