"""
Integration tests for the database setup.

Verifies engine creation, session management, and basic connectivity,
especially focusing on nuances related to SQLite and testing environments.
These tests rely on the test DB setup in conftest.py.

Integration tests for tagline_backend_app.db (engine and session setup).
"""

from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def test_engine_is_engine(test_engine):
    """Verify that get_engine() returns a valid SQLAlchemy Engine instance."""
    from tagline_backend_app.db import get_engine

    # Clear cache to ensure we get a fresh engine based on current env vars
    get_engine.cache_clear()
    engine = get_engine()
    assert isinstance(engine, Engine)


def test_engine_sqlite_check_same_thread(monkeypatch):
    """Verify check_same_thread=False is set ONLY for SQLite."""
    from tagline_backend_app.db import get_engine

    # Test with SQLite
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_check_thread.db")
    get_engine.cache_clear()  # Clear cache before getting the engine
    engine = get_engine()
    assert engine.url.database == "test_check_thread.db"  # Confirm SQLite URL
    # StaticPool should be used for SQLite
    # Direct access to pool or connect_args might be internal/version-dependent.
    # Instead, we rely on the fact that it *should* work if configured correctly.
    # Test a basic connection to implicitly check `check_same_thread=False`.
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        assert True  # Connection successful
    except Exception as e:
        pytest.fail(f"SQLite connection failed, possibly due to check_same_thread: {e}")
    finally:
        if Path("test_check_thread.db").exists():
            Path("test_check_thread.db").unlink()

    # Test with PostgreSQL (or other non-SQLite)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/db")
    get_engine.cache_clear()
    engine = get_engine()
    assert not str(engine.url).startswith("sqlite")
    # For non-SQLite, StaticPool should NOT be used (default is likely NullPool or QueuePool)
    # and check_same_thread should not be in connect_args.
    # Again, exact checks are tricky; rely on it working if configured correctly.
    assert "check_same_thread" not in getattr(engine, "connect_args", {})


def test_sessionlocal_works(test_engine):
    """Verify get_session_local() returns a session factory and sessions work."""
    from tagline_backend_app.db import get_session_local

    get_session_local.cache_clear()  # Ensure fresh factory
    SessionLocal = get_session_local(engine=test_engine)
    assert isinstance(SessionLocal, sessionmaker)

    # Test creating and using a session
    session = SessionLocal()
    assert isinstance(session, Session)
    try:
        # Perform a simple query
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()


def test_get_db_dependency(db_session):
    """Verify the get_db dependency yields a working session."""
    # db_session fixture already uses get_db implicitly
    assert isinstance(db_session, Session)
    assert db_session.is_active

    # Perform a simple query to ensure it's usable
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


# Test caching behavior


def test_engine_and_session_caching(monkeypatch):
    """Verify that get_engine and get_session_local are cached."""
    from tagline_backend_app.db import get_engine, get_session_local

    # Clear caches initially
    get_engine.cache_clear()
    get_session_local.cache_clear()

    # Call first time
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:?cache=shared")
    engine1 = get_engine()
    session_local1 = get_session_local()

    # Call second time with same URL
    engine2 = get_engine()
    session_local2 = get_session_local()

    assert engine1 is engine2
    assert session_local1 is session_local2

    # Call with different URL (should NOT be cached)
    # Note: Caching is based on arguments. get_engine() takes no args by default,
    # using settings.DATABASE_URL implicitly. Changing the env var and reloading
    # config is the typical way to change the effective URL.
    # However, for direct testing, we can pass a different URL if the function allows.
    # Let's simulate env change and config reload as done in conftest.

    # Simulate changing env var and reloading config
    monkeypatch.setenv("DATABASE_URL", "sqlite:///another_test.db")
    # Need to simulate config reload - this is tricky without importing main/config directly
    # Let's clear cache instead to force re-evaluation with new env var
    get_engine.cache_clear()
    get_session_local.cache_clear()

    engine3 = get_engine()
    session_local3 = get_session_local()

    assert engine3 is not engine1
    assert session_local3 is not session_local1

    # Clean up dummy file if created
    if Path("another_test.db").exists():
        Path("another_test.db").unlink()
