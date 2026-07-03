"""
Enterprise Provider Factory.
"""

from __future__ import annotations

import os

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

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if api_key:

            return OpenAIProvider()

        return MockProvider()