"""Base tool interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import ToolCallResult, ToolContext, ToolDefinition


class BaseTool(ABC):
    """A callable tool exposed to the LLM."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Schema used for LLM function calling."""
        ...

    @abstractmethod
    async def execute(
        self, arguments: dict[str, Any], context: ToolContext
    ) -> ToolCallResult:
        """Run the tool with validated arguments."""
        ...

    def validate_arguments(self, arguments: dict[str, Any]) -> list[str]:
        """Return a list of validation errors, empty when valid."""
        errors: list[str] = []

        for param in self.definition.parameters:
            if param.required and param.name not in arguments:
                errors.append(f"Missing required parameter: {param.name}")
            if param.enum and param.name in arguments:
                if arguments[param.name] not in param.enum:
                    errors.append(
                        f"Invalid value for {param.name}: must be one of {param.enum}"
                    )

        return errors