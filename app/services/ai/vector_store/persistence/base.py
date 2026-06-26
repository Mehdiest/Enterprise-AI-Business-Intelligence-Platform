"""
Persistence interface for vector stores.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class BasePersistence(ABC):
    """
    Base persistence interface.
    """

    @abstractmethod
    def exists(self) -> bool:
        """
        Check whether persisted storage exists.
        """
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        index: Any,
        documents: list,
    ) -> None:
        """
        Persist vector index and documents.
        """
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
    ) -> tuple[Any, list]:
        """
        Load persisted vector index and documents.
        """
        raise NotImplementedError