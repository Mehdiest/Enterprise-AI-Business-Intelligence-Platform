"""Application configuration loaded from environment."""

from __future__ import annotations

import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_UNSAFE_SECRETS = {
    "",
    "change-this-secret-key",
    "super-secret-key-change-this",
    "change_this_secret_key",
    "my_super_secret_key",
    "replace-with-a-random-48-byte-token",
}


class Settings(BaseSettings):
    project_name: str = "Enterprise AI Decision Intelligence Platform"
    api_v1_prefix: str = "/api/v1"
    app_env: str = "development"
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    cors_origins: str = "*"
    max_upload_mb: int = 10
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def is_production(self) -> bool:
        """True when running under the production environment."""
        return self.app_env.strip().lower() == "production"

    @property
    def database_url(self) -> str:
        """PostgreSQL SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins split from the comma-separated setting."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _reject_unsafe_secret(self) -> "Settings":
        if self.secret_key.strip() not in _UNSAFE_SECRETS:
            return self

        if self.is_production:
            raise ValueError(
                "SECRET_KEY is unset or a known insecure default; "
                "set a strong random value before running in production."
            )

        logger.warning("SECRET_KEY is an insecure default; acceptable only outside production.")
        return self


settings = Settings()
