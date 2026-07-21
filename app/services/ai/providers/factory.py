"""
Enterprise Provider Factory.
"""

from __future__ import annotations

from app.config import settings

from .base import BaseLLMProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider


class ProviderFactory:
    """
    Returns the appropriate provider
    depending on the current environment.
    """

    @staticmethod
    def create() -> BaseLLMProvider:
        """
        Create configured LLM provider.
        """

        if settings.openai_api_key:
            return OpenAIProvider()

        return MockProvider()