"""
E2E test for GET /smoke-test endpoint with API key authentication.
"""

import os

import pytest
import requests
from dotenv import dotenv_values

pytestmark = pytest.mark.e2e

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Load API key directly from .env file
DOTENV_PATH = os.path.join(os.getcwd(), ".env")
DOTENV = dotenv_values(DOTENV_PATH)
API_KEY = DOTENV.get("TAGLINE_API_KEY")


def test_smoke_test_endpoint():
    """E2E: GET /smoke-test with valid API key should return 200 and status ok."""
    assert (
        API_KEY
    ), f"TAGLINE_API_KEY must be set in the .env file for E2E tests. Looked in {DOTENV_PATH}"
    url = f"{BACKEND_URL}/smoke-test"
    headers = {"x-api-key": API_KEY}
    response = requests.get(url, headers=headers, timeout=5)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("status") == "ok"
    assert "provider" in data
