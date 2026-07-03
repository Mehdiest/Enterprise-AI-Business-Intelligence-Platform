"""
Base memory interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .models import ConversationMessage


class BaseMemory(
    ABC,
):
    """
    Base conversation memory.
    """

    @abstractmethod
    def add(
        self,
        message: ConversationMessage,
    ) -> None:
        ...

    @abstractmethod
    def history(
        self,
    ) -> list[ConversationMessage]:
        ...

    @abstractmethod
    def clear(
        self,
    ) -> None:
        ...