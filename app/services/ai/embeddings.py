"""
Enterprise Embedding Service.

Uses an OpenAI-compatible embedding provider when
an API key is configured. Falls back to a deterministic
local hash-based embedding for keyless environments
(tests, demos, CI).
"""

from __future__ import annotations

import hashlib
import math
import os


class EmbeddingService:
    """
    Generates embeddings using an OpenAI-compatible
    provider, or a deterministic local fallback.
    """

    LOCAL_DIMENSION = 384

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self._use_remote = bool(api_key)
        self._client = None

        if self._use_remote:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)
            self.model = os.getenv(
                "EMBEDDING_MODEL",
                "text-embedding-3-small",
            )

    @property
    def dimension(self) -> int:
        """Return the embedding dimension for the active backend."""
        if self._use_remote:
            # text-embedding-3-small → 1536; allow override
            return int(os.getenv("EMBEDDING_DIMENSION", "1536"))
        return self.LOCAL_DIMENSION

    def encode(self, text: str) -> list[float]:
        if self._use_remote:
            return self._encode_remote(text)
        return self._encode_local(text)

    def encode_many(self, texts: list[str]) -> list[list[float]]:
        if self._use_remote:
            return self._encode_many_remote(texts)
        return [self._encode_local(t) for t in texts]

    # ------------------------------------------------------------------
    # Remote (OpenAI) backend
    # ------------------------------------------------------------------

    def _encode_remote(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def _encode_many_remote(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    # ------------------------------------------------------------------
    # Local deterministic backend (no network, no API key)
    # ------------------------------------------------------------------

    def _encode_local(self, text: str) -> list[float]:
        """Produce a deterministic pseudo-embedding from text.

        Uses SHA-512 hash expanded to LOCAL_DIMENSION floats, then
        L2-normalizes so cosine/IP similarity is meaningful.
        Identical texts always produce identical vectors.
        """
        digest = hashlib.sha512(text.encode("utf-8")).digest()

        # Expand hash bytes to fill LOCAL_DIMENSION floats
        raw: list[float] = []
        seed = digest
        while len(raw) < self.LOCAL_DIMENSION:
            for byte in seed:
                raw.append((byte / 255.0) * 2.0 - 1.0)
                if len(raw) >= self.LOCAL_DIMENSION:
                    break
            seed = hashlib.sha512(seed).digest()

        vector = raw[: self.LOCAL_DIMENSION]

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector