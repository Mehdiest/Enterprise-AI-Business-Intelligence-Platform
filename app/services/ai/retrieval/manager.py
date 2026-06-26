"""
Retriever manager.
"""

from __future__ import annotations

from app.services.ai.retrieval.faiss import (
    FAISSRetriever,
)

from app.services.ai.retrieval.base import (
    BaseRetriever,
)


class RetrievalManager:
    """
    Enterprise retrieval manager.
    """

    _retriever: BaseRetriever | None = None

    @classmethod
    def get(
        cls,
    ) -> BaseRetriever:

        if cls._retriever is None:

            cls._retriever = (
                FAISSRetriever()
            )

        return cls._retriever