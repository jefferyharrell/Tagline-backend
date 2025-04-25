"""
E2E tests for GET /photos/{id} endpoint.
- Uses real backend server, DB, and storage.
- Simulates real HTTP requests and checks responses.
"""

import uuid

import pytest
import requests

API_BASE = "http://localhost:8000"


@pytest.mark.e2e
def test_get_photo_valid_id():
    # Get the first photo from the list endpoint
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip(
            "No photos available for E2E test. Add a photo to storage and rescan."
        )
    photo = items[0]
    photo_id = photo["id"]
    url = f"{API_BASE}/photos/{photo_id}"
    resp = requests.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(photo_id)
    assert "object_key" in data
    assert "metadata" in data and "description" in data["metadata"]
    assert "last_modified" in data


@pytest.mark.e2e
def test_get_photo_invalid_uuid():
    url = f"{API_BASE}/photos/not-a-uuid"
    resp = requests.get(url)
    assert resp.status_code == 422
    assert "detail" in resp.json()


@pytest.mark.e2e
def test_get_photo_nonexistent_id():
    fake_id = uuid.uuid4()
    url = f"{API_BASE}/photos/{fake_id}"
    resp = requests.get(url)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo not found"
