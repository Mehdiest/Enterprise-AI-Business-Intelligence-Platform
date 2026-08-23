"""
Enterprise Vector Store Manager.

Responsible for maintaining a single shared semantic
index during application lifecycle. Supports lazy
initialization on first use and rebuild after data
ingestion.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.vector_store.base import BaseVectorStore
from app.services.ai.vector_store.index_builder import (
    SemanticIndexBuilder,
)

logger = logging.getLogger(__name__)


class VectorManager:
    """
    Singleton manager for semantic search.
    """

    _store: BaseVectorStore | None = None
    _lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def initialize(
        cls,
        db: AsyncSession,
    ) -> None:
        """
        Build semantic index once. Loads from disk
        if a persisted index exists, otherwise builds
        from warehouse data.
        """

        if cls._store is not None:
            return

        async with cls._lock:
            # Double-check after acquiring lock
            if cls._store is not None:
                return

            # Try loading persisted index first
            persisted = SemanticIndexBuilder.load_persisted()
            if persisted is not None:
                cls._store = persisted
                return

            # Build from scratch
            cls._store = await SemanticIndexBuilder(db).build()

    @classmethod
    def get_store(
        cls,
    ) -> BaseVectorStore | None:

        return cls._store

    @classmethod
    async def rebuild(
        cls,
        db: AsyncSession,
    ) -> None:
        """Rebuild the index from warehouse data."""

        async with cls._lock:
            cls._store = await SemanticIndexBuilder(db).build()
            logger.info(
                "Vector index rebuilt | documents=%s",
                cls._store.count() if cls._store else 0,
            )

    @classmethod
    def indexed_documents(
        cls,
    ) -> int:

        if cls._store is None:
            return 0

        return cls._store.count()

    @classmethod
    def reset(cls) -> None:
        """Clear the in-memory store (for tests)."""
        cls._store = None