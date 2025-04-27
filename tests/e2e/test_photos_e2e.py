"""
E2E tests for GET /photos/{id} endpoint.
- Uses real backend server, DB, and storage.
- Simulates real HTTP requests and checks responses.
"""

import uuid

import pytest
import requests

from tests.e2e.auth_utils import get_auth_session

API_BASE = "http://localhost:8000"


# We no longer need this function since we're using cookie auth
# The get_auth_session() from auth_utils.py replaces it


@pytest.mark.e2e
def test_get_photo_valid_id():
    # Get the first photo from the list endpoint (authenticated)
    # Use the authenticated session with cookies instead of tokens
    session = get_auth_session()
    list_url = f"{API_BASE}/photos"
    list_resp = session.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip(
            "No photos available for E2E test. Add a photo to storage and rescan."
        )
    photo = items[0]
    photo_id = photo["id"]
    url = f"{API_BASE}/photos/{photo_id}"
    resp = session.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(photo_id)
    assert "object_key" in data
    assert "metadata" in data and "description" in data["metadata"]
    assert "last_modified" in data


@pytest.mark.e2e
def test_get_photo_invalid_uuid():
    # Use the authenticated session with cookies instead of tokens
    session = get_auth_session()
    url = f"{API_BASE}/photos/not-a-uuid"
    resp = session.get(url)
    assert resp.status_code == 422


@pytest.mark.e2e
def test_get_photo_requires_auth():
    """Requesting /photos without auth should return 401 (cookie-based auth)."""
    list_url = f"{API_BASE}/photos"
    resp = requests.get(list_url)
    assert resp.status_code == 401
    assert "detail" in resp.json()
    assert "detail" in resp.json()


@pytest.mark.e2e
def test_get_photo_nonexistent_id():
    # Use a session with cookies instead of tokens
    session = get_auth_session()
    fake_id = uuid.uuid4()
    resp = session.get(f"{API_BASE}/photos/{fake_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo not found"
