"""Base retriever agent."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.ai.copilot.context_runtime import ExecutionContext


class BaseRetrieverAgent(ABC):
    """Base retrieval interface."""

    @abstractmethod
    async def run(self, context: ExecutionContext) -> ExecutionContext:
        ...
