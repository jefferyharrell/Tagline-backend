"""
Database session management for the Tagline backend.

Handles SQLAlchemy engine and session creation.
Uses SQLAlchemy and configuration from tagline_backend_app.config.
"""

import logging
from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

# Use the new package name for imports
from tagline_backend_app.config import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory, managed by lru_cache for efficiency.
# Caching ensures we reuse the same engine/sessionmaker across the app,
# crucial for performance and consistency, especially with in-memory SQLite.

Base = declarative_base()


@lru_cache()
def get_engine(db_url: str | None = None):
    """Returns a SQLAlchemy engine instance, cached for reuse."""
    settings = get_settings()
    url = db_url or settings.DATABASE_URL
    logger.info(f"Creating SQLAlchemy engine for URL: {settings.DATABASE_URL}")

    connect_args = {}
    poolclass = NullPool  # Default for non-SQLite

    if url and url.startswith("sqlite"):
        # Use StaticPool for ALL SQLite in-memory DBs (including shared cache URIs)
        # This ensures all connections share the same in-memory DB in the same process.
        # Required for reliable testing with sqlite:///:memory: and sqlite:///file::memory:?cache=shared
        poolclass = StaticPool
        connect_args = {"check_same_thread": False}
        logger.info(
            "Configuring SQLite engine with StaticPool and check_same_thread=False for in-memory or shared-cache DB."
        )

    try:
        engine = create_engine(url, poolclass=poolclass, connect_args=connect_args)
        logger.info(
            f"SQLAlchemy engine created successfully. id(engine)={id(engine)}, url={url}"
        )
        return engine
    except Exception as e:
        logger.exception("Failed to create SQLAlchemy engine.")
        raise RuntimeError(f"Failed to create SQLAlchemy engine: {e}")


@lru_cache()
def get_session_local(engine=None):
    """Returns a SQLAlchemy SessionLocal class, cached for reuse."""
    if engine is None:
        engine = get_engine()
    logger.info("Creating SQLAlchemy SessionLocal factory.")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("SQLAlchemy SessionLocal factory created successfully.")
    return SessionLocal


# --- Database Session Dependency ---


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    logger.debug("Database session opened.")
    try:
        yield session
        session.commit()
        logger.debug("Database session committed.")
    except HTTPException:
        # Just rollback and re-raise without logging for expected HTTP exceptions
        session.rollback()
        raise
    except Exception:
        # Log and re-raise other exceptions
        logger.exception("Unexpected exception during DB session, rolling back.")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Database session closed.")


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a SQLAlchemy session."""
    with session_scope() as session:
        yield session


def close_db_connections():
    """Closes database connections associated with the engine."""
    engine = get_engine()
    if hasattr(engine, "dispose"):
        engine.dispose()
        logger.info("Database connections closed.")
    else:
        logger.warning("Engine does not support dispose method.")
