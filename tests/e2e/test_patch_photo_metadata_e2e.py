"""
E2E tests for PATCH /photos/{id}/metadata endpoint.
- Uses real backend server, DB, and storage.
- Simulates real HTTP PATCH requests and checks responses.
- Assumes at least one photo is present in the system.
"""

import uuid

import pytest
import requests

API_BASE = "http://localhost:8000"


@pytest.mark.e2e
def test_patch_photo_metadata_valid():
    # Get a real photo
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo = items[0]
    photo_id = photo["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    new_desc = "E2E updated description"
    patch_resp = requests.patch(patch_url, json={"metadata": {"description": new_desc}})
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["metadata"]["description"] == new_desc
    # Confirm via GET
    get_resp = requests.get(f"{API_BASE}/photos/{photo_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["metadata"]["description"] == new_desc


@pytest.mark.e2e
def test_patch_photo_empty_description():
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo_id = items[0]["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    patch_resp = requests.patch(patch_url, json={"metadata": {"description": ""}})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["metadata"]["description"] == ""


@pytest.mark.e2e
def test_patch_photo_missing_description():
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo_id = items[0]["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    patch_resp = requests.patch(patch_url, json={"metadata": {}})
    assert patch_resp.status_code == 422
    assert "description is required" in patch_resp.json()["detail"]


@pytest.mark.e2e
def test_patch_photo_nonstring_description():
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo_id = items[0]["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    patch_resp = requests.patch(patch_url, json={"metadata": {"description": 123}})
    assert patch_resp.status_code == 422
    assert "description is required" in patch_resp.json()["detail"]


@pytest.mark.e2e
def test_patch_photo_last_modified_valid():
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo_id = items[0]["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    patch_resp = requests.patch(
        patch_url,
        json={
            "metadata": {
                "description": "desc",
                "last_modified": "2025-04-25T12:00:00+00:00",
            }
        },
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["metadata"]["description"] == "desc"
    assert "last_modified" in patch_resp.json()


@pytest.mark.e2e
def test_patch_photo_last_modified_invalid():
    list_url = f"{API_BASE}/photos"
    list_resp = requests.get(list_url)
    assert list_resp.status_code == 200
    items = list_resp.json().get("items", [])
    if not items:
        pytest.skip("No photos available for E2E test. Add a photo and rescan.")
    photo_id = items[0]["id"]
    patch_url = f"{API_BASE}/photos/{photo_id}/metadata"
    patch_resp = requests.patch(
        patch_url,
        json={"metadata": {"description": "desc", "last_modified": "not-a-date"}},
    )
    assert patch_resp.status_code == 422
    assert "last_modified must be RFC3339/ISO8601 string" in patch_resp.json()["detail"]


@pytest.mark.e2e
def test_patch_photo_nonexistent_id():
    fake_id = uuid.uuid4()
    patch_url = f"{API_BASE}/photos/{fake_id}/metadata"
    patch_resp = requests.patch(patch_url, json={"metadata": {"description": "desc"}})
    assert patch_resp.status_code == 404
    assert patch_resp.json()["detail"] == "Photo not found"


@pytest.mark.e2e
def test_patch_photo_invalid_uuid():
    patch_url = f"{API_BASE}/photos/not-a-uuid/metadata"
    patch_resp = requests.patch(patch_url, json={"metadata": {"description": "desc"}})
    assert patch_resp.status_code == 422
    assert "detail" in patch_resp.json()
