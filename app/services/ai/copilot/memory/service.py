"""
Memory service.
"""

from __future__ import annotations

from .models import ConversationMessage
from .repository import MemoryRepository
from .session import ConversationSession
from .store import MemoryStore
from .window import ContextWindow


class MemoryService:
    """
    Enterprise memory service.
    """

    def __init__(self) -> None:

        self.repository = MemoryRepository()
        self.store = MemoryStore()
        self.window = ContextWindow()

    def create_session(
        self,
    ) -> str:

        return str(
            ConversationSession()
        )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        self.store.add(
            session_id,
            ConversationMessage(
                role=role,
                content=content,
            ),
        )

    def history(
        self,
        session_id: str,
    ):

        return self.store.history(
            session_id
        )

    def context(
        self,
        session_id: str,
    ):

        history = self.history(
            session_id
        )

        return self.window.build(
            history
        )

    def clear(
        self,
        session_id: str,
    ) -> None:

        self.store.clear(
            session_id
        )