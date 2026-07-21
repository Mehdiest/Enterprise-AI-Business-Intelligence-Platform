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

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        await self.store.add(
            session_id,
            ConversationMessage(
                role=role,
                content=content,
            ),
        )

    async def history(
        self,
        session_id: str,
    ):

        return await self.store.history(
            session_id
        )

    async def context(
        self,
        session_id: str,
    ):

        history = await self.history(
            session_id
        )

        return self.window.build(
            history
        )

    async def clear(
        self,
        session_id: str,
    ) -> None:

        await self.store.clear(
            session_id
        )
