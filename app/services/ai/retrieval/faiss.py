"""
FAISS retriever.
"""

from __future__ import annotations

from app.services.ai.embeddings import (
    EmbeddingService,
)

from app.services.ai.vector_store.manager import (
    VectorManager,
)

from app.services.ai.retrieval.base import (
    BaseRetriever,
)


class FAISSRetriever(
    BaseRetriever,
):
    """
    Semantic retriever backed by FAISS.
    """

    def __init__(
        self,
    ):
        self.embedding = (
            EmbeddingService()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        store = (
            VectorManager.get_store()
        )

        if store is None:
            return []

        vector = (
            self.embedding.encode(
                query
            )
        )

        return store.search(
            vector,
            top_k=top_k,
        )