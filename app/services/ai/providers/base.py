"""Base LLM provider."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Base interface for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
