"""
Semantic index builder.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

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


class SemanticIndexBuilder:
    """
    Builds enterprise semantic indexes.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store: BaseVectorStore = (
            VectorStoreFactory.create()
        )

    def build(
        self,
    ) -> BaseVectorStore:

        documents: list[
            KnowledgeDocument
        ] = (
            KnowledgeEngine(
                self.db
            ).build()
        )

        if not documents:
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

        return self.vector_store