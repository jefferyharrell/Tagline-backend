"""
config.py

Configuration for the Tagline backend application.
Reads environment variables using Pydantic's BaseSettings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional, cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilesystemProviderSettings(BaseSettings):
    """
    Settings specific to the filesystem storage provider.
    The path is now optional. If unset, provider will raise a runtime error on first use.
    """

    path: Optional[Path] = Field(
        default=None,
        alias="FILESYSTEM_STORAGE_PATH",
        description="Root directory for storing photos. Reads from FILESYSTEM_STORAGE_PATH env var. Optional; if unset, provider will raise on use.",
    )


class Settings(BaseSettings):
    """
    App settings loaded from environment variables.

    Includes authentication and security parameters:
    - BACKEND_PASSWORD: Password for admin or privileged backend actions.
    - JWT_SECRET_KEY: Secret key used to sign JWT tokens (keep this secret and stable!).
    - CORS_ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins (e.g. 'https://frontend.com,https://admin.frontend.com'). If empty or unset, CORS is not enabled (secure default).
    """

    @property
    def COOKIE_SECURE(self) -> bool:
        """Return True only if APP_ENV is 'production' (case-insensitive)."""
        return self.APP_ENV.strip().lower() == "production"

    CORS_ALLOWED_ORIGINS: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins. If empty, CORS is not enabled.",
    )

    APP_ENV: str = Field(
        default="production",
        description="Application environment. Use 'production' for prod, 'development' for dev, 'test' for testing.",
    )

    STORAGE_PROVIDER: str = Field(
        default="filesystem",
        description="Which storage backend to use (e.g., 'filesystem', 's3', 'dropbox'). Defaults to 'filesystem'.",
    )
    DATABASE_URL: str = Field(
        default="sqlite:////data/tagline.db",
        description="Database connection string. Defaults to SQLite file in /data volume if not set.",
    )
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection string for token storage. Must be set in production and development.",
    )
    filesystem_storage: FilesystemProviderSettings = Field(
        default_factory=cast(
            Callable[[], FilesystemProviderSettings], FilesystemProviderSettings
        )
    )
    # Dropbox storage provider settings (flat)
    dropbox_refresh_token: Optional[str] = Field(
        default=None,
        alias="DROPBOX_REFRESH_TOKEN",
        description="Dropbox OAuth2 refresh token (required for server-to-server auth)",
    )
    dropbox_app_key: Optional[str] = Field(
        default=None,
        alias="DROPBOX_APP_KEY",
        description="Dropbox app key (required for refresh token auth)",
    )
    dropbox_app_secret: Optional[str] = Field(
        default=None,
        alias="DROPBOX_APP_SECRET",
        description="Dropbox app secret (required for refresh token auth)",
    )
    dropbox_root_path: Optional[str] = Field(
        default=None,
        alias="DROPBOX_ROOT_PATH",
        description="Root path in Dropbox. All keys are relative to this path.",
    )
    dropbox_access_token: Optional[str] = Field(
        default=None,
        alias="DROPBOX_ACCESS_TOKEN",
        description="[DEPRECATED] Long-lived Dropbox access token. Use refresh token flow instead.",
    )

    TAGLINE_API_KEY: str = Field(
        default="",
        alias="TAGLINE_API_KEY",
        description="API key for backend authentication. Set via TAGLINE_API_KEY env var. Required.",
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Default log level",
    )

    THUMBNAIL_CACHE_MAX_MB: int = Field(
        default=100,
        description="Default thumbnail cache size in MB",
    )
    IMAGE_CACHE_MAX_MB: int = Field(
        default=200,
        description="Default image cache size in MB",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings from environment variables"""
        # If we're in a test environment, set test defaults for auth fields
        import os

        is_test = kwargs.get("APP_ENV", os.environ.get("APP_ENV", "")).lower() == "test"

        if is_test:
            # Don't override if already set
            if kwargs.get("TAGLINE_API_KEY") is None:
                kwargs["TAGLINE_API_KEY"] = "test_api_key_for_testing_only"
            if kwargs.get("REDIS_URL") is None:
                kwargs["REDIS_URL"] = "redis://localhost:6379/1"
            if (
                kwargs.get("DATABASE_URL") is None
                and os.environ.get("DATABASE_URL") is None
            ):
                kwargs["DATABASE_URL"] = "sqlite:///:memory:"

        super().__init__(**kwargs)

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Allow extra env vars without error
    }  # type: ignore[assignment]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings instance."""
    return Settings()  # type: ignore[reportCallIssue]


def clear_settings_cache():
    """Clears the cache for the get_settings() function."""
    get_settings.cache_clear()
    import logging

    logger = logging.getLogger(__name__)
    logger.debug("Cleared get_settings cache.")


__all__ = ["get_settings", "Settings", "clear_settings_cache"]
