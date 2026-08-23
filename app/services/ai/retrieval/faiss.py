"""FAISS-backed semantic retriever."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.embeddings import EmbeddingService
from app.services.ai.retrieval.base import BaseRetriever
from app.services.ai.vector_store.manager import VectorManager

logger = logging.getLogger(__name__)


class FAISSRetriever(BaseRetriever):
    """Semantic retriever backed by the configured vector store."""

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.embedding = EmbeddingService()
        self.db = db

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        # Lazy initialization: build index on first use
        if self.db is not None:
            await VectorManager.initialize(self.db)

        store = VectorManager.get_store()

        if store is None:
            return []

        try:
            embedding = self.embedding.encode(query)
            return store.search(embedding, top_k=top_k)
        except Exception:
            logger.exception("Retrieval failed | query=%s", query)
            return []