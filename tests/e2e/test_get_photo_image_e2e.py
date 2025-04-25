"""
E2E tests for GET /photos/{id}/image endpoint.
Requires backend server running (Docker Compose recommended).
"""

import os
import uuid

import pytest
import requests

pytestmark = pytest.mark.e2e

BACKEND_URL = os.getenv("TAGLINE_BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def test_photo_id():
    # Create a photo via the API (simulate what the backend expects)
    # For E2E, assume a test photo with known ID and image exists, or skip test if not.
    # This is a placeholder for a real setup step.
    # If no setup endpoint exists, skip.
    return os.getenv("TAGLINE_E2E_PHOTO_ID")


def test_get_photo_image_success(test_photo_id):
    if not test_photo_id:
        pytest.skip("No E2E test photo ID set in env; skipping.")
    url = f"{BACKEND_URL}/photos/{test_photo_id}/image"
    resp = requests.get(url)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/")
    assert resp.content  # Should have some bytes


def test_get_photo_image_photo_not_found():
    # Use a random UUID that should not exist
    fake_id = str(uuid.uuid4())
    url = f"{BACKEND_URL}/photos/{fake_id}/image"
    resp = requests.get(url)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo not found"


def test_get_photo_image_invalid_uuid():
    url = f"{BACKEND_URL}/photos/not-a-uuid/image"
    resp = requests.get(url)
    assert resp.status_code == 422
    assert "detail" in resp.json()
