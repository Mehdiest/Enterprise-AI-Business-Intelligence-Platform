"""
Base interface for vector stores.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    """
    Base contract for vector store implementations.
    """

    @abstractmethod
    def add(
        self,
        embeddings: list[list[float]],
        documents: list[str],
    ) -> None:
        """Add embeddings and their documents to the store."""

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        top_k: int = 3,
    ) -> list[dict]:
        """Search for the top-k most similar documents."""

    @abstractmethod
    def count(self) -> int:
        """Return the number of indexed documents."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all indexed documents."""

    def save(self, path: str) -> None:
        """Persist the index to disk. Optional."""
        raise NotImplementedError

    def load(self, path: str) -> None:
        """Load the index from disk. Optional."""
        raise NotImplementedError