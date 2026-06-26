"""
Intent classifier interface.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.services.ai.copilot.intent.models import (
    IntentResult,
)


class BaseIntentClassifier(ABC):
    """
    Base intent classifier.
    """

    @abstractmethod
    def classify(
        self,
        question: str,
    ) -> IntentResult:
        """
        Classify user intent.
        """