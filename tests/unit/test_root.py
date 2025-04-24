"""
Unit tests for the root endpoint in Tagline backend.
Covers both production and development modes.
"""

import importlib
import tempfile
from typing import Any

import httpx
import pytest

from app import config


@pytest.fixture(autouse=True)
def reset_settings_cache():
    config.get_settings.cache_clear()


def test_root_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    config.get_settings.cache_clear()
    # Ensure filesystem path is set for Settings
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tmpdir)
    config.get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    client = TestClient(app)

    import app.routes.root

    importlib.reload(app.routes.root)

    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_explicit_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    config.get_settings.cache_clear()
    # Ensure filesystem path is set for Settings
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tmpdir)
    config.get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    client = TestClient(app)

    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    config.get_settings.cache_clear()
    # Ensure filesystem path is set for Settings
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tmpdir)
    config.get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    client = TestClient(app)

    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["message"].startswith("\U0001F44B Welcome to the Tagline API")
    assert data["app"] == "Tagline"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"
    assert data["redoc"] == "/redoc"


def test_root_env_case_insensitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "DeVeLoPmEnT")
    config.get_settings.cache_clear()
    # Ensure filesystem path is set for Settings
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tmpdir)
    config.get_settings.cache_clear()

    from fastapi.testclient import TestClient

    from app.main import create_app

    app = create_app()
    client = TestClient(app)

    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["app"] == "Tagline"
    assert data["version"] == "0.1.0"
