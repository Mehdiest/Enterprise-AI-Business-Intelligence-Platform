"""
Base interface for Large Language Model providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract interface for all LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response from a prompt.
        """
        raise NotImplementedError