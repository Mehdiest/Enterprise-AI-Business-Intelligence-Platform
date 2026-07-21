"""
Semantic context builder.
"""

from __future__ import annotations

from app.services.ai.copilot.memory import MemoryService
from app.services.ai.copilot.context.models import (
    ContextDocument,
    RetrievalContext,
)
from app.services.ai.retrieval.faiss import (
    FAISSRetriever,
)


class ContextBuilder:
    """
    Enterprise context builder.
    The builder works even if the
    vector index is unavailable.
    """

    def __init__(
        self,
    ) -> None:
        self.memory = MemoryService()
        try:
            self.retriever = (
                FAISSRetriever()
            )
        except Exception:
            self.retriever = None

    async def build(
        self,
        question: str,
        session_id: str | None = None,
        top_k: int = 5,
    ) -> RetrievalContext:

        documents: list[
            ContextDocument
        ] = []
        conversation: list[str] = []

        if session_id is not None:
            conversation = [
                f"{m.role}: {m.content}"
                for m in await self.memory.context(
                    session_id
                )
            ]

        if self.retriever is not None:
            try:
                results = (
                    self.retriever.retrieve(
                        question,
                        top_k=top_k,
                    )
                )
                documents = [
                    ContextDocument(
                        text=item["document"],
                        score=item["score"],
                    )
                    for item in results
                ]
            except Exception:
                documents = []

        return RetrievalContext(
            documents=documents,
            conversation=conversation,
        )
