"""
db.py

Database engine and session setup for the Tagline backend.
Uses SQLAlchemy and configuration from app.config.

- Uses the DATABASE_URL from Pydantic settings for backend-agnostic configuration.
- Handles SQLite-specific options (notably check_same_thread=False) to ensure safe multithreaded access in FastAPI.
- Easily extensible for other backends (Postgres, MySQL, etc.).
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Create the SQLAlchemy engine.
# For SQLite, 'check_same_thread=False' is required to allow connections to be shared across threads.
# This is necessary because FastAPI (and Uvicorn) may handle requests in multiple threads.
# For all other databases, this option is ignored.
engine: Engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if settings.DATABASE_URL.startswith("sqlite")
        else {}
    ),
    future=True,
)

# SessionLocal is the factory for database sessions.
# Always use SessionLocal() to get a session for a request.
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)

__all__ = ["engine", "SessionLocal"]
