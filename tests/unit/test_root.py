"""
Unit tests for the root endpoint in Tagline backend.
Covers both production and development modes.
"""

import importlib
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient


def test_root_production(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_explicit_production(
    monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_development(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.setenv("APP_ENV", "development")
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
    monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    monkeypatch.setenv("APP_ENV", "DeVeLoPmEnT")
    import app.routes.root

    importlib.reload(app.routes.root)
    response: httpx.Response = client.get("/")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["app"] == "Tagline"
    assert data["version"] == "0.1.0"
