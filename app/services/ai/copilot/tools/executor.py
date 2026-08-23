"""Tool registry and dispatcher."""

from __future__ import annotations

import logging

from .base import BaseTool
from .models import ToolCall, ToolCallResult, ToolContext

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Registry mapping tool names to tools; dispatches ToolCall objects."""

    def __init__(self, tools: list[BaseTool] | None = None) -> None:
        self._tools: dict[str, BaseTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.definition.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def definitions(self) -> list[dict]:
        """All tool schemas in OpenAI function-calling format."""
        return [tool.definition.to_json_schema() for tool in self._tools.values()]

    async def dispatch(self, call: ToolCall, context: ToolContext) -> ToolCallResult:
        """Validate arguments and execute the requested tool."""
        tool = self._tools.get(call.tool_name)

        if tool is None:
            logger.warning("Unknown tool requested | name=%s", call.tool_name)
            return ToolCallResult(
                tool_call_id=call.id,
                tool_name=call.tool_name,
                success=False,
                error=f"Unknown tool: {call.tool_name}",
            )

        errors = tool.validate_arguments(call.arguments)
        if errors:
            return ToolCallResult(
                tool_call_id=call.id,
                tool_name=call.tool_name,
                success=False,
                error="; ".join(errors),
            )

        result = await tool.execute(call.arguments, context)
        result.tool_call_id = call.id
        return result