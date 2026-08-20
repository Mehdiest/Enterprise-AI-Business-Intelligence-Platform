"""
Base tool interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ToolContext, ToolResult


class BaseTool(ABC):

    @abstractmethod
    def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        ...