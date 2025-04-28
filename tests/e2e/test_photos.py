"""
E2E test for GET /photos endpoint with API key authentication.
Ensures endpoint returns 200 and a valid response contract (list of photos).
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


def test_get_photos_endpoint():
    """E2E: GET /photos with valid API key returns 200 and a list of photo objects."""
    assert (
        API_KEY
    ), f"TAGLINE_API_KEY must be set in the .env file for E2E tests. Looked in {DOTENV_PATH}"
    url = f"{BACKEND_URL}/photos"
    headers = {"x-api-key": API_KEY}
    response = requests.get(url, headers=headers, timeout=10)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, dict), f"Expected dict, got {type(data)}: {data}"
    assert "items" in data, f"Missing 'items' key in response: {data}"
    assert isinstance(data["items"], list), f"'items' should be a list: {data}"
    # If there are any photos, check structure of the first one
    if data["items"]:
        photo = data["items"][0]
        assert isinstance(photo, dict), f"Photo should be a dict: {photo}"
        for key in ("id", "object_key", "last_modified"):
            assert key in photo, f"Missing key '{key}' in photo: {photo}"
