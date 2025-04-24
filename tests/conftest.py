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
import uuid

import pytest

from app import config
from app.db import get_engine, get_session_local
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def set_global_filesystem_storage_path(tmp_path_factory):
    """
    Ensure FILESYSTEM_STORAGE_PATH is set for all tests unless already set.
    """
    import os

    if not os.environ.get("FILESYSTEM_STORAGE_PATH"):
        photo_storage_dir = tmp_path_factory.mktemp("photos_global")
        os.environ["FILESYSTEM_STORAGE_PATH"] = str(photo_storage_dir)
        config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


@pytest.fixture()
def set_filesystem_storage_path(tmp_path, monkeypatch):
    """Ensure FILESYSTEM_STORAGE_PATH is set for every test and config cache is cleared."""
    temp_photo_dir = tmp_path / "photos"
    temp_photo_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", str(temp_photo_dir))
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


@pytest.fixture()
def ensure_filesystem_path_set(tmp_path, monkeypatch):
    """Fixture to ensure FILESYSTEM_STORAGE_PATH is set for settings validation.
    Does NOT interact with the database session.
    """
    temp_photo_dir = tmp_path / "photos_config_test"
    temp_photo_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", str(temp_photo_dir))
    config.get_settings.cache_clear()
    yield
    # Clean up env var potentially? Or rely on monkeypatch auto-cleanup.
    config.get_settings.cache_clear()


@pytest.fixture(scope="session", autouse=True)
def configure_test_session_db():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    # Reload config and db AFTER setting the env var
    importlib.reload(config)


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
def db_session(monkeypatch, set_filesystem_storage_path):
    """Creates a new, fully isolated in-memory SQLite DB and returns a session."""
    unique_name = f"test_{uuid.uuid4().hex}"
    db_url = f"sqlite:///file:{unique_name}?mode=memory&cache=shared&uri=true"
    monkeypatch.setenv("DATABASE_URL", db_url)
    import importlib

    import app.config as config

    importlib.reload(config)
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = get_session_local()
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
def client(tmp_path_factory):
    """Reusable FastAPI TestClient for the app."""
    import os
    import uuid

    # Set up a unique shared in-memory SQLite DB URI
    unique_name = f"test_{uuid.uuid4().hex}"
    db_url = f"sqlite:///file:{unique_name}?mode=memory&cache=shared&uri=true"
    os.environ["DATABASE_URL"] = db_url
    # Set up a unique temp directory for the filesystem provider
    photo_storage_dir = tmp_path_factory.mktemp("photos")
    os.environ["FILESYSTEM_STORAGE_PATH"] = str(photo_storage_dir)
    # Clear config cache AFTER setting env vars
    from app.config import get_settings

    get_settings.cache_clear()
    # Now import DB/models and create tables
    from app.db import get_engine
    from app.models import Base

    engine = get_engine()
    Base.metadata.create_all(engine)
    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    return TestClient(app)
