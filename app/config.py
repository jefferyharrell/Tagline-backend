"""
config.py

Configuration for the Tagline backend application.
Reads environment variables using Pydantic's BaseSettings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    DATABASE_URL: str = Field(
        default="sqlite:///./tagline.db",
        description="Database connection string. Defaults to SQLite local file if not set.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
