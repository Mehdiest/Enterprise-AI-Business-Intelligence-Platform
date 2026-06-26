"""
FAISS vector store implementation.
"""

from __future__ import annotations

import faiss
import numpy as np

from app.services.ai.vector_store.base import BaseVectorStore


class FAISSVectorStore(BaseVectorStore):
    """
    FAISS implementation of BaseVectorStore.
    """

    def __init__(
        self,
        dimension: int = 384,
    ):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.documents: list[str] = []

    def add(
        self,
        embeddings: list[list[float]],
        documents: list[str],
    ) -> None:

        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        self.index.add(vectors)

        self.documents.extend(documents)

    def search(
        self,
        embedding: list[float],
        top_k: int = 3,
    ) -> list[dict]:

        vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            vector,
            top_k,
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0],
        ):

            if idx == -1:
                continue

            results.append(
                {
                    "document": self.documents[idx],
                    "score": round(
                        float(score),
                        4,
                    ),
                }
            )

        return results

    def count(self) -> int:

        return len(
            self.documents
        )

    def clear(self) -> None:

        self.index.reset()

        self.documents.clear()