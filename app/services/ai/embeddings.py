"""
Enterprise Embedding Service.

Uses an embedding provider instead of
local transformer models.
"""

from __future__ import annotations

from openai import OpenAI
import os


class EmbeddingService:
    """
    Generates embeddings using
    an OpenAI-compatible provider.
    """

    def __init__(self) -> None:

        self.client = OpenAI(
            api_key=os.getenv(
                "OPENAI_API_KEY"
            )
        )

        self.model = os.getenv(
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )

    def encode(
        self,
        text: str,
    ) -> list[float]:

        response = (
            self.client.embeddings.create(
                model=self.model,
                input=text,
            )
        )

        return response.data[0].embedding

    def encode_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        response = (
            self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
        )

        return [
            item.embedding
            for item in response.data
        ]