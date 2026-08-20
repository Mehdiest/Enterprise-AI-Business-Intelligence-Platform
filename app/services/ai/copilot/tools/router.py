"""
Enterprise Tool Router.
"""

from __future__ import annotations

from .models import ToolContext, ToolResult


class ToolRouter:
    """
    Routes requests to specialized tools.

    Phase 6:
    No tool is implemented yet.
    """

    def dispatch(
        self,
        context: ToolContext,
    ) -> ToolResult:

        return ToolResult(
            handled=False,
            answer=None,
        )