"""
Semantic context builder.
"""

from __future__ import annotations

from app.services.ai.retrieval.faiss import (
    FAISSRetriever,
)

from app.services.ai.copilot.context.models import (
    ContextDocument,
    RetrievalContext,
)


class ContextBuilder:
    """
    Builds semantic retrieval context.
    """

    def __init__(
        self,
    ):
        self.retriever = (
            FAISSRetriever()
        )

    def build(
        self,
        question: str,
        top_k: int = 5,
    ) -> RetrievalContext:

        results = (
            self.retriever.retrieve(
                question,
                top_k=top_k,
            )
        )

        return RetrievalContext(
            documents=[
                ContextDocument(
                    text=item["document"],
                    score=item["score"],
                )
                for item in results
            ]
        )