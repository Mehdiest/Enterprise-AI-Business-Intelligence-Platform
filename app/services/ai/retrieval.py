"""
Semantic retrieval service.

Responsible for retrieving the most
relevant knowledge using vector search.
"""

from __future__ import annotations

from app.services.ai.embeddings import EmbeddingService
from app.services.ai.vector_store import VectorManager


class RetrievalService:
    """
    Enterprise semantic retrieval service.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[str]:
        """
        Retrieve relevant documents.
        """

        query = query.strip()

        if not query:
            return []

        embedding = self.embedding_service.encode(
            query
        )

        store = VectorManager.get_store()

        results = store.search(
            embedding,
            top_k=top_k,
        )

        return results