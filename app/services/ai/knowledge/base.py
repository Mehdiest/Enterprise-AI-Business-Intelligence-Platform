"""
Base interface for all knowledge builders.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.schemas.knowledge import KnowledgeDocument


class BaseKnowledgeBuilder(ABC):
    """
    Base contract for enterprise
    knowledge builders.
    """

    @abstractmethod
    def build(
        self,
    ) -> list[KnowledgeDocument]:
        """
        Build structured knowledge documents.
        """