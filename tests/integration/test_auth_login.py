"""
Integration tests for the login authentication flow using FastAPI TestClient (no HTTP layer).
"""

import os

import pytest
from fastapi import status

from tagline_backend_app.deps import get_token_store
from tests.test_utils.token_store import InMemoryTokenStore

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


@pytest.mark.integration
def test_logout_revokes_token(test_client):
    """Verify that logout removes the refresh token from the token store."""
    # 1. Setup a specific token store for this test and override dependency
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override

    try:
        # 2. Login to populate the store and get cookies
        login_response = test_client.post("/login", json={"password": BACKEND_PASSWORD})
        assert login_response.status_code == status.HTTP_200_OK
        login_cookies = login_response.cookies
        refresh_token = login_cookies.get("tagline_refresh_token")
        assert refresh_token is not None

        # 3. Verify the token exists in the store *before* logout
        assert token_store_override.is_refresh_token_valid(refresh_token) is True

        # 4. Set cookies on the client directly, call logout, then clear cookies
        test_client.cookies.clear()  # Clear any existing cookies to avoid pollution
        for k, v in login_cookies.items():
            test_client.cookies.set(k, v)
        logout_response = test_client.post("/logout")
        assert logout_response.status_code == 200
        assert logout_response.json() == {"detail": "Successfully logged out"}
        test_client.cookies.clear()  # Clean up after ourselves

        # 5. Verify the token is *revoked* (not valid) in the store *after* logout
        assert token_store_override.is_refresh_token_valid(refresh_token) is False

    finally:
        # Clean up the dependency override
        test_client.app.dependency_overrides.pop(get_token_store, None)
