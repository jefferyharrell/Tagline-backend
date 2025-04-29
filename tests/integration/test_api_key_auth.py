"""
Integration tests for API Key Authentication.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tagline_backend_app.config import get_settings

pytestmark = pytest.mark.integration


def test_protected_endpoint_missing_api_key(test_client: TestClient):
    """Verify accessing a protected endpoint without API key returns 401 Unauthorized."""
    response = test_client.get("/photos")  # Use any protected endpoint
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing API Key" in response.json()["detail"]


def test_protected_endpoint_invalid_api_key(test_client: TestClient):
    """Verify accessing a protected endpoint with invalid API key returns 403 Forbidden."""
    headers = {"x-api-key": "invalid-api-key-value"}
    response = test_client.get("/photos", headers=headers)  # Use any protected endpoint
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Invalid API Key" in response.json()["detail"]


def test_protected_endpoint_valid_api_key(test_client: TestClient):
    """Verify accessing a protected endpoint with valid API key succeeds."""
    api_key = get_settings().TAGLINE_API_KEY
    headers = {"x-api-key": api_key}

    # Use the smoke-test endpoint which is our health check endpoint
    response = test_client.get("/smoke-test", headers=headers)
    assert response.status_code == status.HTTP_200_OK  # Success means auth worked


def test_scan_missing_api_key(test_client: TestClient):
    """POST /scan with no API key returns 401 Unauthorized."""
    response = test_client.post("/scan")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing API Key" in response.json()["detail"]


def test_scan_invalid_api_key(test_client: TestClient):
    """POST /scan with invalid API key returns 403 Forbidden."""
    headers = {"x-api-key": "invalid-api-key-value"}
    response = test_client.post("/scan", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Invalid API Key" in response.json()["detail"]


def test_scan_valid_api_key(test_client: TestClient):
    """POST /scan with valid API key returns 200 and valid placeholder response."""
    api_key = get_settings().TAGLINE_API_KEY
    headers = {"x-api-key": api_key}
    response = test_client.post("/scan", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.json()
