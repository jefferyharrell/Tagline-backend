"""
Unit tests for the /login endpoint.
Covers: valid login (happy path).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def valid_password():
    # Import get_settings only after pytest fixtures have set up the environment
    from app.config import get_settings

    settings = get_settings()
    assert (
        settings.BACKEND_PASSWORD is not None
    ), "BACKEND_PASSWORD is not set in test settings"
    return settings.BACKEND_PASSWORD


def test_login_valid(client: TestClient, valid_password):
    """
    Test that a valid password returns 200 and both access and refresh tokens.
    """
    response = client.post("/login", json={"password": valid_password})
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert "access_token" in data, "access_token missing in response"
    assert "refresh_token" in data, "refresh_token missing in response"
    assert (
        isinstance(data["access_token"], str) and data["access_token"]
    ), "access_token should be non-empty string"
    assert (
        isinstance(data["refresh_token"], str) and data["refresh_token"]
    ), "refresh_token should be non-empty string"
