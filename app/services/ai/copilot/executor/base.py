"""Base execution engine."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.ai.copilot.context_runtime import ExecutionContext


class BaseExecutor(ABC):
    """Abstract execution engine."""

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionContext:
        """Execute an execution context."""
        ...