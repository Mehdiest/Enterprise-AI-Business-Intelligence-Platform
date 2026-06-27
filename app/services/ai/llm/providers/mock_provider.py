"""
Mock LLM provider.

Used during development before integrating
real language models.
"""

from __future__ import annotations

from app.services.ai.llm.base import (
    BaseLLMProvider,
)


class MockProvider(
    BaseLLMProvider,
):
    """
    Simple development provider.
    """

    def generate(
        self,
        prompt: str,
    ) -> str:

        return (
            "Mock LLM Response\n\n"
            "Prompt received successfully."
        )