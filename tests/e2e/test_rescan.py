"""
E2E test for POST /rescan endpoint with API key authentication.
Ensures endpoint returns 200 and a valid response contract.
"""

import os

import pytest
import requests
from dotenv import dotenv_values

pytestmark = pytest.mark.e2e

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
DOTENV_PATH = os.path.join(os.getcwd(), ".env")
DOTENV = dotenv_values(DOTENV_PATH)
API_KEY = DOTENV.get("TAGLINE_API_KEY")


def test_rescan_endpoint():
    """E2E: POST /rescan with valid API key returns 200 and valid contract."""
    assert (
        API_KEY
    ), f"TAGLINE_API_KEY must be set in the .env file for E2E tests. Looked in {DOTENV_PATH}"
    url = f"{BACKEND_URL}/rescan"
    headers = {"x-api-key": API_KEY}
    response = requests.post(url, headers=headers, timeout=10)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, dict), f"Expected dict, got {type(data)}: {data}"
    assert "imported" in data, f"Missing 'imported' key: {data}"
    assert "imported_count" in data, f"Missing 'imported_count' key: {data}"
    assert isinstance(data["imported"], list), f"'imported' should be a list: {data}"
    assert isinstance(
        data["imported_count"], int
    ), f"'imported_count' should be int: {data}"
    # Optionally: imported_count should match len(imported)
    assert data["imported_count"] == len(
        data["imported"]
    ), f"imported_count ({data['imported_count']}) does not match len(imported) ({len(data['imported'])})"
