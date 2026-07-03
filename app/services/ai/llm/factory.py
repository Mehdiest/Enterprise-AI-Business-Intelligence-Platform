"""
LLM Factory.
"""

from __future__ import annotations

from app.services.ai.providers import (
    ProviderFactory,
)


class LLMFactory:
    """
    Enterprise LLM Factory.
    """

    @staticmethod
    def create():

        return ProviderFactory.create()