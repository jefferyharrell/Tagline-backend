"""
session.py

FastAPI dependency for providing a SQLAlchemy session per request.

Usage:
    from app.db.session import get_db

    @app.get("/some-route")
    def some_route(db: Session = Depends(get_db)):
        ...

This ensures that each request gets its own session and that sessions are properly closed.
"""

from typing import Generator

from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy session per request and ensures it is closed after use.
    Yields:
        Session: SQLAlchemy session object.
    """
    from app.db import get_session_local

    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()
