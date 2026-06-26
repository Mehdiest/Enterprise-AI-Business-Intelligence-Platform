"""
Enterprise Vector Store Manager.

Responsible for maintaining a single
shared semantic index during application
lifecycle.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.ai.vector_store.base import BaseVectorStore
from app.services.ai.vector_store.index_builder import (
    SemanticIndexBuilder,
)


class VectorManager:
    """
    Singleton manager for semantic search.
    """

    _store: BaseVectorStore | None = None

    @classmethod
    def initialize(
        cls,
        db: Session,
    ) -> None:
        """
        Build semantic index once.
        """

        if cls._store is None:

            cls._store = (
                SemanticIndexBuilder(
                    db
                ).build()
            )

    @classmethod
    def get_store(
        cls,
    ) -> BaseVectorStore:

        if cls._store is None:

            raise RuntimeError(
                "Vector index is not initialized."
            )

        return cls._store

    @classmethod
    def rebuild(
        cls,
        db: Session,
    ) -> None:

        cls._store = (
            SemanticIndexBuilder(
                db
            ).build()
        )

    @classmethod
    def indexed_documents(
        cls,
    ) -> int:

        if cls._store is None:
            return 0

        return cls._store.count()