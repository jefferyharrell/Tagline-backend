"""
E2E tests for the login authentication flow.
"""

import os
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file using pathlib
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

BACKEND_PASSWORD_RAW = os.getenv("BACKEND_PASSWORD")
if not BACKEND_PASSWORD_RAW:
    raise RuntimeError("BACKEND_PASSWORD is not set in the environment or .env file!")
# Clean the value (remove comments, whitespace)
BACKEND_PASSWORD = BACKEND_PASSWORD_RAW.strip().split()[0]

pytestmark = pytest.mark.e2e

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/login"


@pytest.mark.asyncio
async def test_login_success():
    """Test login with valid credentials returns access and refresh tokens."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            LOGIN_ENDPOINT,
            json={
                "password": BACKEND_PASSWORD.strip().split()[
                    0
                ]  # Support comments after value
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "Login successful"
        # Check that both auth cookies are set
        cookies = response.cookies
        assert cookies, "No cookies set by backend"
        assert "tagline_access_token" in cookies, "Missing tagline_access_token cookie"
        assert (
            "tagline_refresh_token" in cookies
        ), "Missing tagline_refresh_token cookie"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials returns 401 Unauthorized."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(LOGIN_ENDPOINT, json={"password": "wrongpassword"})
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Invalid password"
