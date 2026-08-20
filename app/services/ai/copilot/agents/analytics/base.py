"""Base analytics agent."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.ai.copilot.context_runtime import ExecutionContext


class BaseAnalyticsAgent(ABC):
    """Base analytics interface."""

    @abstractmethod
    def run(self, context: ExecutionContext) -> ExecutionContext:
        ...
