"""
config.py

Configuration for the Tagline backend application.
Reads environment variables using Pydantic's BaseSettings.
"""

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional, cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilesystemProviderSettings(BaseSettings):
    """
    Settings specific to the filesystem storage provider.
    """

    path: Path = Field(
        ...,
        alias="FILESYSTEM_STORAGE_PATH",
        description="Root directory for storing photos. Reads from FILESYSTEM_STORAGE_PATH env var.",
    )


class DropboxProviderSettings(BaseSettings):
    """
    Settings for Dropbox photo storage provider (NOT IMPLEMENTED).
    """

    access_token: str = Field(
        default="",
        alias="DROPBOX_ACCESS_TOKEN",
        description="Access token for Dropbox API (not yet implemented)",
    )
    root_path: str = Field(
        default="/",
        alias="DROPBOX_ROOT_PATH",
        description="Root path in Dropbox (not yet implemented)",
    )


class Settings(BaseSettings):
    """
    App settings loaded from environment variables.

    Includes authentication and security parameters:
    - BACKEND_PASSWORD: Password for admin or privileged backend actions.
    - JWT_SECRET_KEY: Secret key used to sign JWT tokens (keep this secret and stable!).
    """

    APP_ENV: str = Field(
        default="production",
        description="Application environment. Use 'production' for prod, 'development' for dev, 'test' for testing.",
    )

    STORAGE_PROVIDER: str = Field(
        default="filesystem",
        description="Which storage backend to use (e.g., 'filesystem', 's3', 'dropbox'). Defaults to 'filesystem'.",
    )
    DATABASE_URL: str = Field(
        default="sqlite:///./tagline.db",
        description="Database connection string. Defaults to SQLite local file if not set.",
    )
    filesystem_photo_storage: FilesystemProviderSettings = Field(
        default_factory=cast(
            Callable[[], FilesystemProviderSettings], FilesystemProviderSettings
        )
    )
    dropbox_photo_storage: Optional[DropboxProviderSettings] = None

    BACKEND_PASSWORD: Optional[str] = Field(
        default=None,  # Will be set in __init__ for test environments
        description="Password for backend authentication. Set via BACKEND_PASSWORD env var. Required in production.",
    )
    JWT_SECRET_KEY: Optional[str] = Field(
        default=None,  # Will be set in __init__ for test environments
        description="Secret key for signing JWT tokens. Set via JWT_SECRET_KEY env var. Must be long, random, and kept secret in production.",
    )

    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(
        default=900,
        description="Access token expiration time in seconds. Defaults to 900 (15 minutes). Override with ACCESS_TOKEN_EXPIRE_SECONDS env var.",
    )
    REFRESH_TOKEN_EXPIRE_SECONDS: int = Field(
        default=604800,
        description="Refresh token expiration time in seconds. Defaults to 604800 (7 days). Override with REFRESH_TOKEN_EXPIRE_SECONDS env var.",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings from environment variables"""
        # If we're in a test environment, set test defaults for auth fields
        is_test = kwargs.get("APP_ENV", "").lower() == "test" or "pytest" in sys.modules

        if is_test:
            # Don't override if already set
            if kwargs.get("BACKEND_PASSWORD") is None:
                kwargs["BACKEND_PASSWORD"] = "test_password"
            if kwargs.get("JWT_SECRET_KEY") is None:
                kwargs["JWT_SECRET_KEY"] = "test_jwt_secret_key_not_for_production"

        super().__init__(**kwargs)

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }  # type: ignore[assignment]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[reportCallIssue]
