"""LLM provider factory."""

from __future__ import annotations

from app.config import settings

from .base import BaseLLMProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider


class ProviderFactory:
    """Select an LLM provider based on configuration."""

    @staticmethod
    def create() -> BaseLLMProvider:
        """Return the OpenAI provider when a key is set, else the mock provider."""
        if settings.openai_api_key:
            return OpenAIProvider()

        return MockProvider()
