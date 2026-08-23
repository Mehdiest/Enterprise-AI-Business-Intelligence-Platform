"""OpenAI chat-completions provider."""

from __future__ import annotations

import logging
import os

from openai import OpenAI, AuthenticationError, RateLimitError, APIError

from app.config import settings

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Generate text using the OpenAI chat-completions API.

    Supports any OpenAI-compatible endpoint (Router, DeepInfra,
    Together AI, Azure, local vLLM, etc.) via environment variables.
    
    Required Environment Variables (set in .env or docker-compose.yml):
        - OPENAI_API_KEY: Your API key
        - OPENAI_BASE_URL: (Optional) Custom endpoint URL
        - OPENAI_MODEL: (Optional) Model name
    """

    def __init__(self):
        # Get credentials from environment ONLY (never hardcoded!)
        api_key = (
            settings.openai_api_key 
            or os.getenv("OPENAI_API_KEY", "").strip()
        )
        
        base_url = (
            os.getenv("OPENAI_BASE_URL", "").strip() 
            or getattr(settings, 'openai_base_url', None)
        )
        
        model = (
            os.getenv("OPENAI_MODEL", "").strip()
            or getattr(settings, 'openai_model', None)
            or "gpt-3.5-turbo"  # Safe default
        )
        
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or docker-compose.yml"
            )
        
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model
        
        logger.info("OpenAI Provider initialized | model=%s | base_url=%s", 
                   self.model, (base_url or "default")[:50])

    def generate(self, prompt: str) -> str:
        """Generate a response with robust error handling."""
        
        logger.debug("Generating response | model=%s | prompt_length=%d", 
                    self.model, len(prompt))
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            
            # Validate response structure
            if not completion.choices:
                logger.error("API returned empty choices | completion=%s", completion)
                raise APIError(
                    "LLM provider returned empty response. "
                    "This may indicate: 1) Token quota exceeded, 2) Model overloaded, "
                    "3) Invalid API key. Please check your provider dashboard."
                )
            
            message = completion.choices[0].message
            if not message:
                logger.error("API returned empty message | choice=%s", completion.choices[0])
                raise APIError("LLM provider returned empty message object.")
                
            content = message.content
            
            if content is None or not content.strip():
                logger.warning("API returned empty/None content")
                return (
                    "I'm sorry, I couldn't generate a response right now. "
                    "The AI service may be experiencing high demand or your token quota "
                    "may have been exhausted. Please try again in a few minutes."
                )
            
            logger.info("Response generated successfully | length=%d", len(content))
            return content
            
        except AuthenticationError as e:
            logger.exception("Authentication failed with LLM provider")
            raise APIError(
                f"Authentication failed with LLM provider. "
                f"Please check your API key is valid. Error: {e}"
            ) from e
            
        except RateLimitError as e:
            logger.exception("Rate limit exceeded with LLM provider")
            raise APIError(
                f"Rate limit exceeded. Your token quota for today may be exhausted. "
                f"Please check your Router dashboard or try again later. Error: {e}"
            ) from e
            
        except APIError as e:
            # Re-raise our custom API errors
            raise
            
        except Exception as e:
            logger.exception("Unexpected error calling LLM provider")
            raise APIError(
                f"Unexpected error from LLM provider: {type(e).__name__}: {e}"
            ) from e
