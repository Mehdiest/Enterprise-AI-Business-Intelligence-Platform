"""
Mock LLM provider.

Used automatically when no API key
is configured.
"""

from __future__ import annotations

from .base import BaseLLMProvider


class MockProvider(BaseLLMProvider):

    def generate(
        self,
        prompt: str,
    ) -> str:

        return (
            "Mock AI Response\n\n"
            "OpenAI API Key is not configured.\n"
            "Copilot is running in development mode.\n\n"
            "Planner, Memory, Agents and Context "
            "pipeline executed successfully."
        )