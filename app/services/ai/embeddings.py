"""
Embedding service using Sentence Transformers.

Provides semantic vector generation for business text.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates sentence embeddings for semantic search.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    def encode(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate embedding vector for a single sentence.
        """
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    def encode_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return vectors.tolist()