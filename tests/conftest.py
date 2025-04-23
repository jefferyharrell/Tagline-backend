"""
Shared pytest fixtures and configuration for Tagline backend tests.
- Ensures app package is importable (fixes sys.path).
- Provides a reusable TestClient fixture.
- Manages APP_ENV environment variable for test isolation.
"""

import os
import sys

# Ensure Tagline-backend is on sys.path FIRST
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config, db
from app.main import app
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def configure_test_session_db():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    # Reload config and db AFTER setting the env var
    importlib.reload(config)
    importlib.reload(db)


# NOTE FOR FUTURE DEVELOPERS (AND AI CODING ASSISTANTS):
#
# This fixture uses the classic `sqlite:///:memory:` URI, which is perfect for single-connection tests.
# If you ever need to share an in-memory DB across multiple connections (e.g., for integration tests
# with FastAPI's TestClient or multi-threaded scenarios), use the following URI format:
#   sqlite:///file:unique_name?mode=memory&cache=shared&uri=true
# ...where unique_name is unique per test (e.g., via uuid or pytest's request.node.name).
# See: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#shared-memory
#
# Only switch to this approach if you actually need shared state across DB connections!


@pytest.fixture(scope="function")
def db_session():
    """Creates a new in-memory SQLite DB and returns a session.
    See comment above for shared-in-memory-DB advice.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session


@pytest.fixture(autouse=True)
def reset_app_env():
    """Reset APP_ENV after each test to avoid cross-test contamination."""
    original = os.environ.get("APP_ENV")
    yield
    if original is not None:
        os.environ["APP_ENV"] = original
    else:
        os.environ.pop("APP_ENV", None)


@pytest.fixture(scope="session")
def client():
    """Reusable FastAPI TestClient for the app."""
    return TestClient(app)
