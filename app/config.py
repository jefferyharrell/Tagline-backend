"""
config.py

Configuration for the Tagline backend application.
Reads environment variables using Pydantic's BaseSettings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilesystemProviderSettings(BaseSettings):
    """
    Settings specific to the filesystem storage provider.
    """

    path: Path = Field(
        ...,
        alias="FILESYSTEM_PHOTO_STORAGE_PATH",
        description="Root directory for storing photos. Reads from FILESYSTEM_PHOTO_STORAGE_PATH env var.",
    )


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

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

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings from environment variables"""
        super().__init__(**kwargs)

    model_config: SettingsConfigDict = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }  # type: ignore[assignment]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[reportCallIssue]
