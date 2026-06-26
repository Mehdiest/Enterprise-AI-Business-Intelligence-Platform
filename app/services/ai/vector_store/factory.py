"""
Vector store factory.

Creates vector store implementations.
"""

from __future__ import annotations

from app.services.ai.vector_store.base import BaseVectorStore
from app.services.ai.vector_store.faiss_store import FAISSVectorStore


class VectorStoreFactory:
    """
    Factory for vector store providers.
    """

    DEFAULT_PROVIDER = "faiss"

    @classmethod
    def create(
        cls,
        provider: str | None = None,
    ) -> BaseVectorStore:

        provider = (
            provider
            or cls.DEFAULT_PROVIDER
        ).lower()

        if provider == "faiss":
            return FAISSVectorStore()

        raise ValueError(
            f"Unsupported vector provider: {provider}"
        )