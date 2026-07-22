"""TTL-bound, database-backed conversation memory."""

from __future__ import annotations

import asyncio
import sqlite3
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import settings

from .models import ConversationMessage


class MemoryStore:
    def __init__(
        self, database_path: str | None = None, ttl_seconds: int | None = None
    ) -> None:
        self.database_path = Path(database_path or settings.memory_database_path)
        self.ttl = timedelta(seconds=ttl_seconds or settings.memory_ttl_seconds)
        self._lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(
            self.database_path, 
            timeout=10, 
            check_same_thread=False
        )
        connection.row_factory = sqlite3.Row
        # Enable WAL to prevent database locks in multi-worker deployments.
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        return connection

    def _initialize(self) -> None:
        """Create table and index at construction."""
        with self._lock, self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS conversation_memory (
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )"""
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS ix_memory_expiry ON conversation_memory(expires_at)"
            )

    async def add(self, session_id: str, message: ConversationMessage) -> None:
        await asyncio.to_thread(self._add_sync, session_id, message)

    async def history(self, session_id: str) -> list[ConversationMessage]:
        return await asyncio.to_thread(self._history_sync, session_id)

    async def clear(self, session_id: str) -> None:
        await asyncio.to_thread(self._clear_sync, session_id)

    async def collect_garbage(self) -> int:
        return await asyncio.to_thread(self._collect_garbage_sync)

    def _add_sync(self, session_id: str, msg: ConversationMessage) -> None:
        current_time = datetime.now(UTC)
        expires_at = current_time + self.ttl
        timestamp = (
            msg.timestamp.replace(tzinfo=UTC)
            if msg.timestamp.tzinfo is None
            else msg.timestamp
        )
        with self._lock, self._connect() as conn:
            self._purge(conn, current_time)
            conn.execute(
                "INSERT INTO conversation_memory(session_id, role, content, timestamp, expires_at) VALUES (?, ?, ?, ?, ?)",
                (
                    session_id,
                    msg.role,
                    msg.content,
                    timestamp.isoformat(),
                    expires_at.isoformat(),
                ),
            )

    def _history_sync(self, session_id: str) -> list[ConversationMessage]:
        current_time = datetime.now(UTC)
        with self._lock, self._connect() as conn:
            self._purge(conn, current_time)
            rows = conn.execute(
                "SELECT role, content, timestamp FROM conversation_memory WHERE session_id = ? ORDER BY rowid",
                (session_id,),
            ).fetchall()
        
        return [
            ConversationMessage(
                role=row["role"],
                content=row["content"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
            )
            for row in rows
        ]

    def _clear_sync(self, session_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "DELETE FROM conversation_memory WHERE session_id = ?", (session_id,)
            )

    def _collect_garbage_sync(self) -> int:
        with self._lock, self._connect() as conn:
            return self._purge(conn, datetime.now(UTC))

    @staticmethod
    def _purge(conn: sqlite3.Connection, now: datetime) -> int:
        result = conn.execute(
            "DELETE FROM conversation_memory WHERE expires_at <= ?", (now.isoformat(),)
        )
        return result.rowcount