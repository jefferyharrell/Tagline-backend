"""
Integration tests for the /smoke-test endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


@pytest.mark.integration
def test_smoke_test_ok(monkeypatch):
    """Returns 200 and provider info if storage provider is configured."""
    with monkeypatch.context() as m:
        m.setenv("STORAGE_PROVIDER", "filesystem")
        m.setenv("FILESYSTEM_STORAGE_PATH", "/tmp")
        get_settings.cache_clear()
        app = create_app()
        client = TestClient(app)
        response = client.get("/smoke-test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["provider"] == "FilesystemStorageProvider"


@pytest.mark.integration
def test_smoke_test_misconfigured(monkeypatch):
    """Returns 503 if provider is misconfigured (missing env var)."""
    with monkeypatch.context() as m:
        m.setenv("STORAGE_PROVIDER", "filesystem")
        m.delenv("FILESYSTEM_STORAGE_PATH", raising=False)
        get_settings.cache_clear()
        app = create_app()
        client = TestClient(app)
        response = client.get("/smoke-test")
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "StorageProviderMisconfigured"
        assert "FILESYSTEM_STORAGE_PATH is not set" in data["detail"]
