"""Semantic context builder resilient to an unavailable vector index."""

from __future__ import annotations

import logging

from app.services.ai.copilot.context.models import ContextDocument, RetrievalContext
from app.services.ai.copilot.memory import MemoryService
from app.services.ai.retrieval.faiss import FAISSRetriever

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build retrieval context from memory and the vector index."""

    def __init__(self) -> None:
        self.memory = MemoryService()
        try:
            self.retriever = FAISSRetriever()
        except Exception:
            logger.exception("Vector retriever unavailable; running without retrieval.")
            self.retriever = None

    async def build(
        self,
        question: str,
        session_id: str | None = None,
        top_k: int = 5,
    ) -> RetrievalContext:
        conversation = await self._conversation(session_id)
        documents = self._retrieve(question, top_k)

        return RetrievalContext(documents=documents, conversation=conversation)

    async def _conversation(self, session_id: str | None) -> list[str]:
        """Return prior turns for `session_id`, or an empty list."""
        if session_id is None:
            return []

        turns = await self.memory.context(session_id)
        return [f"{turn.role}: {turn.content}" for turn in turns]

    def _retrieve(self, question: str, top_k: int) -> list[ContextDocument]:
        """Retrieve documents; return an empty list if retrieval fails."""
        if self.retriever is None:
            return []

        try:
            hits = self.retriever.retrieve(question, top_k=top_k)
        except (KeyError, RuntimeError, ValueError):
            logger.exception("Retrieval failed | question=%s", question)
            return []

        return [
            ContextDocument(text=hit["document"], score=hit["score"]) for hit in hits
        ]
