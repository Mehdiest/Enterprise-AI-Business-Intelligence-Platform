"""Base retrieval interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    """Base interface for all retrievers."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve relevant documents for a query."""
