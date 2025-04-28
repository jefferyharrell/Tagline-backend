"""
Integration tests for the login authentication flow using FastAPI TestClient (no HTTP layer).
"""

import os

import pytest
from fastapi.testclient import TestClient

BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
# Clean the value (remove comments, whitespace)
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]


@pytest.fixture(scope="session")
def client():
    from tagline_backend_app.main import create_app

    return TestClient(create_app())


BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
# Clean the value (remove comments, whitespace)
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]


@pytest.mark.integration
def test_login_success(client):
    """Test login with valid credentials returns access and refresh tokens as cookies."""
    response = client.post("/login", json={"password": BACKEND_PASSWORD})
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Login successful"
    cookies = response.cookies
    assert cookies, "No cookies set by backend"
    assert "tagline_access_token" in cookies, "Missing tagline_access_token cookie"
    assert "tagline_refresh_token" in cookies, "Missing tagline_refresh_token cookie"


@pytest.mark.integration
def test_login_invalid_credentials(client):
    """Test login with invalid credentials returns 401 Unauthorized."""
    response = client.post("/login", json={"password": "wrongpassword"})
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid password"
