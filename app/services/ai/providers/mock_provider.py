"""Mock LLM provider used when no API key is configured."""

from __future__ import annotations

from .base import BaseLLMProvider

_DEV_NOTICE = (
    "AI Copilot is running in development mode "
    "(no LLM API key configured)."
)


class MockProvider(BaseLLMProvider):

    def generate(self, prompt: str) -> str:
        """Echo the warehouse Data block, or a dev-mode notice."""

        data_block = self._extract_data_section(prompt)

        if data_block:
            return f"Based on the warehouse data:\n{data_block}"

        return _DEV_NOTICE

    @staticmethod
    def _extract_data_section(prompt: str) -> str:
        """Return the text of the Data block in the prompt, if present."""

        if "Data:\n" not in prompt:
            return ""

        after_marker = prompt.split("Data:\n", 1)[1]
        return after_marker.split("\n\nAnswer:", 1)[0].strip()
