"""
Unit tests for app.db (engine and session setup).
"""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app import db


def test_engine_is_engine():
    assert isinstance(db.engine, Engine)


def test_engine_sqlite_check_same_thread():
    # This test assumes the default config is SQLite
    assert db.engine.url.get_backend_name() == "sqlite"
    assert db.engine.url.database == ":memory:"
    # Actually connect to ensure the engine works (and connect_args were correct)
    from sqlalchemy import text

    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_sessionlocal_works():
    session = db.SessionLocal()
    assert isinstance(session, Session)
    session.close()
