"""
db.py

Database engine and session setup for the Tagline backend.
Uses SQLAlchemy and configuration from app.config.

- Uses the DATABASE_URL from Pydantic settings for backend-agnostic configuration.
- Handles SQLite-specific options (notably check_same_thread=False) to ensure safe multithreaded access in FastAPI.
- Easily extensible for other backends (Postgres, MySQL, etc.).
"""

# Create the SQLAlchemy engine.
# For SQLite, 'check_same_thread=False' is required to allow connections to be shared across threads.
# This is necessary because FastAPI (and Uvicorn) may handle requests in multiple threads.
# For all other databases, this option is ignored.
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.DATABASE_URL,
        connect_args=(
            {"check_same_thread": False}
            if settings.DATABASE_URL.startswith("sqlite")
            else {}
        ),
        future=True,
    )


@lru_cache(maxsize=1)
def get_session_local() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(), autoflush=False, autocommit=False, class_=Session
    )


__all__ = ["get_engine", "get_session_local"]
