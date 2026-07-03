"""
Session memory store.
"""

from __future__ import annotations

from .models import ConversationMessage


class MemoryStore:
    """
    Stores conversations by session.
    """

    def __init__(self) -> None:
        self._store: dict[
            str,
            list[ConversationMessage],
        ] = {}

    def add(
        self,
        session_id: str,
        message: ConversationMessage,
    ) -> None:

        self._store.setdefault(
            session_id,
            []
        ).append(message)

    def history(
        self,
        session_id: str,
    ) -> list[ConversationMessage]:

        return list(
            self._store.get(
                session_id,
                []
            )
        )

    def clear(
        self,
        session_id: str,
    ) -> None:

        self._store.pop(
            session_id,
            None,
        )