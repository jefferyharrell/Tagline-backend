"""
E2E tests for the /refresh endpoint.
"""

import os

import pytest
import requests
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")


@pytest.mark.e2e
def test_refresh_valid_login_and_refresh():
    # Step 1: Create a new session and login
    session = requests.Session()
    password = os.getenv("BACKEND_PASSWORD")
    assert password, "BACKEND_PASSWORD not found in environment or .env file"
    login_resp = session.post(f"{API_URL}/login", json={"password": password})
    assert login_resp.status_code == 200

    # Store the initial cookies for comparison
    initial_access_token = session.cookies.get("tagline_access_token")
    initial_refresh_token = session.cookies.get("tagline_refresh_token")
    assert initial_access_token, "Access token cookie not set after login"
    assert initial_refresh_token, "Refresh token cookie not set after login"

    # Step 2: Call refresh endpoint - we don't need to provide the token in the body
    # as it will be sent in the cookie automatically
    refresh_resp = session.post(f"{API_URL}/refresh")
    assert refresh_resp.status_code == 200
    assert refresh_resp.json()["detail"] == "Token refreshed successfully"

    # Check that new cookies were set with different values
    new_access_token = session.cookies.get("tagline_access_token")
    new_refresh_token = session.cookies.get("tagline_refresh_token")
    assert (
        new_access_token != initial_access_token
    ), "Access token cookie did not change"
    assert (
        new_refresh_token != initial_refresh_token
    ), "Refresh token cookie did not change"


@pytest.mark.e2e
def test_refresh_revoked_token_cannot_be_used():
    """
    E2E: After a refresh token is used, it is revoked and cannot be used again.
    """
    # Step 1: Create a new session and login
    session = requests.Session()
    password = os.getenv("BACKEND_PASSWORD")
    assert password, "BACKEND_PASSWORD not found in environment or .env file"
    login_resp = session.post(f"{API_URL}/login", json={"password": password})
    assert login_resp.status_code == 200

    # Capture the refresh token from the cookie for our manual attempt later
    refresh_token_cookie = session.cookies.get("tagline_refresh_token")
    assert refresh_token_cookie, "Refresh token cookie not set"

    # Step 2: Use the refresh endpoint which should revoke the current refresh token
    refresh_resp = session.post(f"{API_URL}/refresh")
    assert refresh_resp.status_code == 200

    # Step 3: Create a new session and try to use the old refresh token
    # (We need to manually set it since it's been revoked and replaced)
    new_session = requests.Session()
    # Manually set the old (now revoked) refresh token
    new_session.cookies.set("tagline_refresh_token", refresh_token_cookie)

    # Try to use the revoked token
    second_resp = new_session.post(f"{API_URL}/refresh")
    assert second_resp.status_code == 401
    assert "Invalid or expired refresh token" in second_resp.text


@pytest.mark.e2e
def test_refresh_invalid_token():
    # Test with no cookies (no auth)
    resp = requests.post(f"{API_URL}/refresh")
    assert resp.status_code == 401

    # Test with an invalid token
    session = requests.Session()
    session.cookies.set("tagline_refresh_token", "not-a-valid-token")
    resp = session.post(f"{API_URL}/refresh")
    assert resp.status_code == 401
