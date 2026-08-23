"""
Semantic index builder.

Builds the FAISS vector index from warehouse knowledge
documents and persists it to disk for fast restarts.
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.knowledge import KnowledgeDocument
from app.services.ai.embeddings import (
    EmbeddingService,
)
from app.services.ai.knowledge.engine import (
    KnowledgeEngine,
)
from app.services.ai.vector_store import (
    VectorStoreFactory,
)
from app.services.ai.vector_store.base import (
    BaseVectorStore,
)

logger = logging.getLogger(__name__)

STORAGE_DIR = Path("storage/vector")
INDEX_PATH = STORAGE_DIR / "index.faiss"
DOCUMENTS_PATH = STORAGE_DIR / "documents.pkl"


class SemanticIndexBuilder:
    """
    Builds enterprise semantic indexes.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store: BaseVectorStore = (
            VectorStoreFactory.create(
                dimension=self.embedding_service.dimension,
            )
        )

    async def build(
        self,
    ) -> BaseVectorStore:

        documents: list[
            KnowledgeDocument
        ] = await (
            KnowledgeEngine(
                self.db
            ).build()
        )

        if not documents:
            logger.info("No knowledge documents to index.")
            return self.vector_store

        texts = [
            document.text
            for document in documents
        ]

        embeddings = (
            self.embedding_service.encode_many(
                texts
            )
        )

        self.vector_store.add(
            embeddings=embeddings,
            documents=texts,
        )

        self._persist()

        logger.info(
            "Semantic index built | documents=%s",
            len(texts),
        )

        return self.vector_store

    def _persist(self) -> None:
        """Save the index and documents to disk."""
        try:
            STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            self.vector_store.save(str(INDEX_PATH))
            with open(DOCUMENTS_PATH, "wb") as f:
                pickle.dump(self.vector_store.documents, f)
        except Exception:
            logger.exception("Failed to persist vector index.")

    @classmethod
    def load_persisted(cls) -> BaseVectorStore | None:
        """Load a previously persisted index, or None if unavailable."""
        if not INDEX_PATH.exists() or not DOCUMENTS_PATH.exists():
            return None

        try:
            from app.services.ai.vector_store.faiss_store import FAISSVectorStore

            store = FAISSVectorStore()
            store.load(str(INDEX_PATH))
            with open(DOCUMENTS_PATH, "rb") as f:
                store.documents = pickle.load(f)

            if store.count() == 0:
                return None

            logger.info(
                "Loaded persisted vector index | documents=%s",
                store.count(),
            )
            return store
        except Exception:
            logger.exception("Failed to load persisted vector index.")
            return None