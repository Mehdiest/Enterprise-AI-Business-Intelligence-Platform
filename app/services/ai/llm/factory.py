"""
LLM provider factory.
"""

from __future__ import annotations

from app.services.ai.llm.base import (
    BaseLLMProvider,
)

from app.services.ai.llm.providers import (
    MockProvider,
)


class LLMFactory:
    """
    Creates LLM providers.
    """

    @staticmethod
    def create() -> BaseLLMProvider:

        return MockProvider()