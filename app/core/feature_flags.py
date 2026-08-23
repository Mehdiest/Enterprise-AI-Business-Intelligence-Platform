"""Feature flags for enabling optional platform capabilities."""

from __future__ import annotations


class FeatureFlags:
    """Toggle optional features."""

    ENABLE_SQL_AGENT = True
    ENABLE_TOOL_CALLING = True
    ENABLE_RAG = True
    ENABLE_ANALYTICS = True
    ENABLE_STREAMING = False
    ENABLE_RESPONSE_CACHE = False
    ENABLE_PROMPT_LOGGING = False
    ENABLE_DEBUG_MODE = False
