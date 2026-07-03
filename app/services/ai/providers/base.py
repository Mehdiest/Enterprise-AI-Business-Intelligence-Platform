"""
Base LLM provider.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        ...