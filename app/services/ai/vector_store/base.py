"""
Abstract vector store interface.

All vector database implementations must inherit
from this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseVectorStore(ABC):
    """
    Base interface for vector databases.
    """

    @abstractmethod
    def add(
        self,
        embeddings: list[list[float]],
        documents: list[str],
    ) -> None:
        """
        Store vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        top_k: int = 3,
    ) -> list[dict]:
        """
        Perform similarity search.
        """
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """
        Number of indexed documents.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all indexed vectors.
        """
        raise NotImplementedError