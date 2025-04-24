"""
End-to-end tests for the /login endpoint using a running dev server (Docker).

Assumes the dev server is up and running (see Justfile for commands).
"""

import os

import pytest
import requests
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")


@pytest.mark.e2e
def test_login_valid():
    """Test that a valid password returns tokens from the live /login endpoint."""
    # Now os.getenv will read the value loaded from .env
    password = os.getenv("BACKEND_PASSWORD")
    # Add an assertion to ensure the password was actually loaded
    assert password, "BACKEND_PASSWORD not found in environment or .env file"
    payload = {"password": password}
    resp = requests.post(f"{API_URL}/login", json=payload, timeout=5)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["expires_in"], int)
    assert isinstance(data["refresh_expires_in"], int)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "bad_payload,expected_status",
    [
        ({}, 422),
        ({"password": 123}, 422),
        ({"password": "wrong"}, 401),
    ],
)
def test_login_invalid(bad_payload, expected_status):
    """Test invalid login payloads and credentials against live /login endpoint."""
    resp = requests.post(f"{API_URL}/login", json=bad_payload, timeout=5)
    assert (
        resp.status_code == expected_status
    ), f"Expected {expected_status}, got {resp.status_code}: {resp.text}"
