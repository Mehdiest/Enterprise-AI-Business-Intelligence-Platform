"""TTL-bound, Postgres-backed conversation memory."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import SessionLocal
from app.models.conversation import ConversationTurn

from .models import ConversationMessage


class MemoryStore:
    """Persist conversation turns in Postgres with TTL expiry."""

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self.ttl = timedelta(seconds=ttl_seconds or settings.memory_ttl_seconds)

    async def add(self, session_id: str, message: ConversationMessage) -> None:
        """Persist one turn and purge expired rows in the same transaction."""
        async with SessionLocal() as session, session.begin():
            await self._purge(session)
            session.add(
                ConversationTurn(
                    session_id=session_id,
                    role=message.role,
                    content=message.content,
                    expires_at=datetime.now(UTC) + self.ttl,
                )
            )

    async def history(self, session_id: str) -> list[ConversationMessage]:
        """Return non-expired turns for a session in insertion order."""
        async with SessionLocal() as session:
            turns = await session.scalars(
                select(ConversationTurn)
                .where(
                    ConversationTurn.session_id == session_id,
                    ConversationTurn.expires_at > datetime.now(UTC),
                )
                .order_by(ConversationTurn.created_at)
            )
            return [
                ConversationMessage(
                    role=turn.role,
                    content=turn.content,
                    timestamp=turn.created_at,
                )
                for turn in turns.all()
            ]

    async def clear(self, session_id: str) -> None:
        """Delete every turn in a session."""
        async with SessionLocal() as session, session.begin():
            await session.execute(
                delete(ConversationTurn).where(
                    ConversationTurn.session_id == session_id
                )
            )

    async def collect_garbage(self) -> int:
        """Delete expired turns; return how many were removed."""
        async with SessionLocal() as session, session.begin():
            return await self._purge(session)

    async def _purge(self, session: AsyncSession) -> int:
        """Delete expired turns; return the removed row count."""
        deleted = await session.execute(
            delete(ConversationTurn).where(
                ConversationTurn.expires_at <= datetime.now(UTC)
            )
        )
        return deleted.rowcount or 0