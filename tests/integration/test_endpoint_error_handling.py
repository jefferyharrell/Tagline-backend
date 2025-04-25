"""
Integration test: endpoint returns clear error if storage provider is misconfigured
"""

import pytest
from fastapi.testclient import TestClient

from tagline_backend_app.config import get_settings
from tagline_backend_app.main import create_app


@pytest.mark.integration
def test_root_endpoint_returns_503_if_storage_provider_misconfigured(monkeypatch):
    """
    If FILESYSTEM_STORAGE_PATH is missing, the root endpoint should return 503 with a clear error.
    """
    monkeypatch.setenv("STORAGE_PROVIDER", "filesystem")
    monkeypatch.delenv("FILESYSTEM_STORAGE_PATH", raising=False)
    get_settings.cache_clear()
    app = create_app()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 503
    data = response.json()
    assert data["error"] == "StorageProviderMisconfigured"
    assert "FILESYSTEM_STORAGE_PATH is not set" in data["detail"]
