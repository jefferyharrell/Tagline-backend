"""
Integration tests for the login authentication flow using FastAPI TestClient (no HTTP layer).
"""

import os

import pytest

BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
# Clean the value (remove comments, whitespace)
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]


# Use the test_client fixture from conftest.py instead
# It properly sets up mocking and dependency overrides


BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
# Clean the value (remove comments, whitespace)
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]


@pytest.mark.integration
def test_login_success(test_client):
    """Test login with valid credentials returns access and refresh tokens as cookies."""
    response = test_client.post("/login", json={"password": BACKEND_PASSWORD})
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Login successful"
    cookies = response.cookies
    assert cookies, "No cookies set by backend"
    assert "tagline_access_token" in cookies, "Missing tagline_access_token cookie"
    assert "tagline_refresh_token" in cookies, "Missing tagline_refresh_token cookie"


@pytest.mark.integration
def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials returns 401 Unauthorized."""
    response = test_client.post("/login", json={"password": "wrongpassword"})
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid password"
