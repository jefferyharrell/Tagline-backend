"""
Integration tests for /refresh endpoint and protected resource access using FastAPI TestClient.
"""

import os
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from tagline_backend_app.db import get_db
from tagline_backend_app.deps import get_token_store
from tests.test_utils.token_store import InMemoryTokenStore

BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]


@pytest.mark.integration
def test_refresh_valid_token_issues_new_tokens(test_client):
    """POST /refresh with valid refresh token issues new tokens (cookie and body)."""
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override
    try:
        # Login to get cookies
        login_resp = test_client.post("/login", json={"password": BACKEND_PASSWORD})
        assert login_resp.status_code == 200
        cookies = login_resp.cookies
        refresh_token = cookies.get("tagline_refresh_token")
        assert refresh_token
        # Call /refresh
        test_client.cookies.set("tagline_refresh_token", refresh_token)
        refresh_resp = test_client.post("/refresh")
        assert refresh_resp.status_code == 200
        data = refresh_resp.json()
        assert "detail" in data
        # New cookies should be set
        new_access = refresh_resp.cookies.get("tagline_access_token")
        new_refresh = refresh_resp.cookies.get("tagline_refresh_token")
        assert new_access, "No new access token cookie set"
        assert new_refresh, "No new refresh token cookie set"
    finally:
        test_client.app.dependency_overrides.pop(get_token_store, None)


@pytest.mark.integration
def test_refresh_invalid_token_returns_401(test_client):
    """POST /refresh with invalid/expired token returns 401."""
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override
    try:
        # Set an invalid refresh token
        test_client.cookies.set("tagline_refresh_token", "totallybogus")
        resp = test_client.post("/refresh")
        assert resp.status_code == 401
        data = resp.json()
        assert "detail" in data
    finally:
        test_client.app.dependency_overrides.pop(get_token_store, None)


@pytest.mark.integration
def test_access_protected_with_valid_access_token(test_client):
    """Access protected endpoint with valid access token (cookie) returns 200."""
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    def get_db_override():
        return MagicMock()

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override
    test_client.app.dependency_overrides[get_db] = get_db_override

    try:
        login_resp = test_client.post("/login", json={"password": BACKEND_PASSWORD})
        assert login_resp.status_code == 200
        cookies = login_resp.cookies
        access_token = cookies.get("tagline_access_token")
        assert access_token
        # Set access token cookie
        test_client.cookies.set("tagline_access_token", access_token)
        resp = test_client.get("/photos")
        assert resp.status_code == 200
    finally:
        test_client.app.dependency_overrides.pop(get_token_store, None)
        test_client.app.dependency_overrides.pop(get_db, None)


@pytest.mark.integration
def test_access_protected_with_missing_or_invalid_token_returns_401(test_client):
    """Access protected endpoint with missing/invalid token returns 401."""
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    def get_db_override():
        return None

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override
    test_client.app.dependency_overrides[get_db] = get_db_override

    try:
        # No token at all
        test_client.cookies.clear()
        resp = test_client.get("/photos")
        assert resp.status_code == 401
        # Invalid token
        test_client.cookies.set("tagline_access_token", "notavalidtoken")
        resp2 = test_client.get("/photos")
        assert resp2.status_code == 401
    finally:
        test_client.app.dependency_overrides.pop(get_token_store, None)
        test_client.app.dependency_overrides.pop(get_db, None)


@pytest.mark.integration
def test_access_token_expiry_requires_refresh(test_client, monkeypatch):
    """Access token expires after configured time; refresh required."""
    token_store_override = InMemoryTokenStore()

    def get_token_store_override():
        return token_store_override

    def get_db_override():
        return MagicMock()

    test_client.app.dependency_overrides[get_token_store] = get_token_store_override
    test_client.app.dependency_overrides[get_db] = get_db_override

    try:
        login_resp = test_client.post("/login", json={"password": BACKEND_PASSWORD})
        assert login_resp.status_code == 200
        cookies = login_resp.cookies
        access_token = cookies.get("tagline_access_token")
        refresh_token = cookies.get("tagline_refresh_token")
        assert access_token and refresh_token
        # Simulate expiry by monkeypatching AuthService.validate_token
        from tagline_backend_app.auth_service import AuthService

        # Save the original method
        original_validate_token = AuthService.validate_token

        # Create a wrapper function for the monkeypatch
        def mock_validate_token(self, token, token_type="access"):
            if token_type == "access":
                # If it's an access token check, simulate expiry
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Simulated token expiry for access token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                # For refresh tokens, call the original validation logic
                # Need to bind `self` back if calling directly on the saved method
                return original_validate_token(self, token, token_type=token_type)

        # Apply the smarter monkeypatch
        monkeypatch.setattr(AuthService, "validate_token", mock_validate_token)

        test_client.cookies.set("tagline_access_token", access_token)
        resp = test_client.get("/photos")
        assert resp.status_code == 401
        # Now refresh token should still work
        test_client.cookies.set("tagline_refresh_token", refresh_token)
        refresh_resp = test_client.post("/refresh")
        assert refresh_resp.status_code == 200
    finally:
        test_client.app.dependency_overrides.pop(get_token_store, None)
        test_client.app.dependency_overrides.pop(get_db, None)
