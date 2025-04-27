"""
Unit tests for tagline_backend_app.db
Covers: get_engine, get_session_local, session_scope, close_db_connections
"""

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from tagline_backend_app.db import (
    close_db_connections,
    get_engine,
    get_session_local,
    session_scope,
)

pytestmark = pytest.mark.unit


def test_get_engine_sqlite_memory(monkeypatch):
    # Should create a StaticPool engine for sqlite:///:memory:
    engine = get_engine("sqlite:///:memory:")
    assert isinstance(engine, Engine)
    # Should use StaticPool
    assert "StaticPool" in str(type(engine.pool))
    close_db_connections()


def test_get_engine_postgres(monkeypatch):
    # Should create a NullPool engine for postgres URLs
    engine = get_engine("postgresql://user:pass@localhost/db")
    assert isinstance(engine, Engine)
    assert "NullPool" in str(type(engine.pool))
    close_db_connections()


def test_get_session_local_returns_sessionmaker(monkeypatch):
    engine = get_engine("sqlite:///:memory:")
    SessionLocal = get_session_local(engine)
    assert isinstance(SessionLocal, sessionmaker)
    close_db_connections()


def test_session_scope_commit(monkeypatch):
    get_session_local(get_engine("sqlite:///:memory:"))
    with session_scope() as session:
        assert isinstance(session, Session)
    close_db_connections()


def test_session_scope_rollback(monkeypatch):
    get_session_local(get_engine("sqlite:///:memory:"))

    class CustomException(Exception):
        pass

    with pytest.raises(CustomException):
        with session_scope():
            raise CustomException()
    close_db_connections()


def test_close_db_connections(monkeypatch):
    get_engine("sqlite:///:memory:")
    # Should not raise
    close_db_connections()
