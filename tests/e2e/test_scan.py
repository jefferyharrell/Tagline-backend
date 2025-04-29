"""
E2E test for POST /scan endpoint with API key authentication.
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


def test_scan_endpoint():
    """
    E2E: POST /scan with valid API key returns 200 and valid contract.
    As of 2025-04-29, /scan is async/idempotent:
      - Returns {"status": "started"} if scan is triggered
      - Returns {"status": "already_running"} if scan is in progress
    In the future, scan results will be available via /health or a similar endpoint.
    """
    assert (
        API_KEY
    ), f"TAGLINE_API_KEY must be set in the .env file for E2E tests. Looked in {DOTENV_PATH}"
    url = f"{BACKEND_URL}/scan"
    headers = {"x-api-key": API_KEY}
    response = requests.post(url, headers=headers, timeout=10)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, dict), f"Expected dict, got {type(data)}: {data}"
    assert "status" in data, f"Missing 'status' key: {data}"
    assert data["status"] in {
        "started",
        "already_running",
    }, f"Unexpected status: {data['status']}"
    # TODO: When scan results are available via /health, add follow-up checks here.
