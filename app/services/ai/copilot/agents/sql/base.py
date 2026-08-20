"""Base SQL agent."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.ai.copilot.context_runtime import ExecutionContext


class BaseSQLAgent(ABC):
    """Base SQL interface."""

    @abstractmethod
    def run(self, context: ExecutionContext) -> ExecutionContext:
        ...
