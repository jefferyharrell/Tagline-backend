"""
E2E tests for GET /photos/{id} endpoint.
- Uses real backend server, DB, and storage.
- Simulates real HTTP requests and checks responses.
"""

import uuid

import pytest
import requests

API_BASE = "http://localhost:8000"


def get_access_token():
    import os

    password = os.getenv("BACKEND_PASSWORD")
    assert password, "BACKEND_PASSWORD not found in environment or .env file"
    resp = requests.post(f"{API_BASE}/login", json={"password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.mark.e2e
def test_get_photo_valid_id():
    # Get the first photo from the list endpoint (authenticated)
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url, headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip(
            "No photos available for E2E test. Add a photo to storage and rescan."
        )
    photo = items[0]
    photo_id = photo["id"]
    url = f"{API_BASE}/photos/{photo_id}"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(photo_id)
    assert "object_key" in data
    assert "metadata" in data and "description" in data["metadata"]
    assert "last_modified" in data


@pytest.mark.e2e
def test_get_photo_invalid_uuid():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE}/photos/not-a-uuid"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 422


@pytest.mark.e2e
def test_get_photo_requires_auth():
    """Requesting /photos without auth should return 403 (FastAPI HTTPBearer default)."""
    list_url = f"{API_BASE}/photos"
    resp = requests.get(list_url)
    assert resp.status_code == 403
    assert "detail" in resp.json()
    assert "detail" in resp.json()


@pytest.mark.e2e
def test_get_photo_nonexistent_id():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = uuid.uuid4()
    url = f"{API_BASE}/photos/{fake_id}"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo not found"
