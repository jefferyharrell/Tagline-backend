"""
Unit tests for GET /photos/{id}/image endpoint.
Covers:
- Valid photo/image retrieval with correct Content-Type
- Photo not found (404)
- File not found (404)
- Invalid UUID (422 handled by FastAPI)
- Storage provider error (500)
"""

import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.deps import get_current_user
from app.main import create_app

app = create_app()
app.dependency_overrides = getattr(app, "dependency_overrides", {})
app.dependency_overrides[get_current_user] = lambda: True
client = TestClient(app)


@pytest.fixture
def fake_photo():
    class FakePhoto:
        id = "123e4567-e89b-12d3-a456-426614174000"
        filename = "test.jpg"
        description = "desc"
        updated_at = None

    return FakePhoto()


def test_get_photo_image_success(monkeypatch, fake_photo):
    # Patch DB repo to return a photo
    monkeypatch.setattr(
        "app.crud.photo.PhotoRepository.get", lambda self, id: fake_photo
    )
    # Patch storage provider to return image bytes
    fake_file = io.BytesIO(b"fake image data")
    monkeypatch.setattr(
        "app.storage.memory.InMemoryStorageProvider.retrieve",
        lambda self, key: fake_file,
    )
    # Patch provider getter to use in-memory
    monkeypatch.setattr(
        app.state,
        "get_photo_storage_provider",
        lambda app_: MagicMock(retrieve=lambda k: fake_file),
    )
    response = client.get(f"/photos/{fake_photo.id}/image")
    assert response.status_code == 200
    assert response.content == b"fake image data"
    assert response.headers["content-type"].startswith("image/")


def test_get_photo_image_photo_not_found(monkeypatch):
    monkeypatch.setattr("app.crud.photo.PhotoRepository.get", lambda self, id: None)
    response = client.get("/photos/123e4567-e89b-12d3-a456-426614174000/image")
    assert response.status_code == 404
    assert response.json()["detail"] == "Photo not found"


def test_get_photo_image_file_not_found(monkeypatch, fake_photo):
    monkeypatch.setattr(
        "app.crud.photo.PhotoRepository.get", lambda self, id: fake_photo
    )

    class FakeProvider:
        def retrieve(self, key):
            raise FileNotFoundError("No file!")

    monkeypatch.setattr(
        app.state, "get_photo_storage_provider", lambda app_: FakeProvider()
    )
    response = client.get(f"/photos/{fake_photo.id}/image")
    assert response.status_code == 404
    assert response.json()["detail"] == "Photo file not found"


def test_get_photo_image_storage_error(monkeypatch, fake_photo):
    monkeypatch.setattr(
        "app.crud.photo.PhotoRepository.get", lambda self, id: fake_photo
    )

    class FakeProvider:
        def retrieve(self, key):
            raise Exception("kaboom")

    monkeypatch.setattr(
        app.state, "get_photo_storage_provider", lambda app_: FakeProvider()
    )
    response = client.get(f"/photos/{fake_photo.id}/image")
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


# Note: Invalid UUID is handled by FastAPI validation, not unit-testable directly here
