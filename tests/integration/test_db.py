"""
Unit tests for app.db (engine and session setup).
"""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def test_engine_is_engine():
    from app.db import get_engine

    assert isinstance(get_engine(), Engine)


def test_engine_sqlite_check_same_thread():
    # This test assumes the default config is SQLite
    from app.db import get_engine

    engine = get_engine()
    assert engine.url.get_backend_name() == "sqlite"
    # Check that the db_session fixture set the expected URI format
    assert str(engine.url).startswith("sqlite:///file:test_")
    # Actually connect to ensure the engine works (and connect_args were correct)
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_sessionlocal_works():
    from app.db import get_session_local

    session = get_session_local()()
    assert isinstance(session, Session)
    session.close()
