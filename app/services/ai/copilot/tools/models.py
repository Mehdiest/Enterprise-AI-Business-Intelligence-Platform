"""Tool-calling domain models."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ToolParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    name: str
    type: ToolParameterType = ToolParameterType.STRING
    description: str = ""
    required: bool = True
    enum: list[str] | None = None


class ToolDefinition(BaseModel):
    """Schema exposed to the LLM for function calling."""

    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)

    def to_json_schema(self) -> dict[str, Any]:
        """Render as an OpenAI function-calling schema."""
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in self.parameters:
            prop: dict[str, Any] = {
                "type": param.type.value,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class ToolCall(BaseModel):
    """A tool invocation requested by the LLM."""

    id: str = ""
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    """Outcome of executing a single tool call."""

    tool_call_id: str = ""
    tool_name: str
    success: bool = True
    output: Any = None
    error: str | None = None

    def to_context_string(self) -> str:
        """Serialize for inclusion in a follow-up prompt."""
        if not self.success:
            return f"Tool '{self.tool_name}' failed: {self.error}"
        if isinstance(self.output, str):
            return self.output
        return json.dumps(self.output, default=str, ensure_ascii=False)


class ToolContext(BaseModel):
    question: str
    session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)