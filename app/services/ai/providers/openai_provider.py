"""OpenAI chat-completions provider."""

from __future__ import annotations

import os

from openai import OpenAI

from app.config import settings

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Generate text using the OpenAI chat-completions API."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def generate(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
