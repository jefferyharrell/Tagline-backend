"""
Unit tests for GET /photos/{id} endpoint in Tagline backend.
Covers: valid photo, invalid UUID, nonexistent photo.
"""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tagline_backend_app.deps import get_current_user
from tagline_backend_app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides = getattr(app, "dependency_overrides", {})
    app.dependency_overrides[get_current_user] = lambda: True
    return TestClient(app)


@pytest.fixture
def mock_photo():
    from datetime import datetime

    class MockPhoto:
        def __init__(self, id, filename, description, updated_at):
            self.id = id
            self.filename = filename
            self.description = description
            self.updated_at = updated_at

    return MockPhoto(
        id=uuid.uuid4(),
        filename="dog.jpg",
        description="A dog",
        updated_at=datetime(2025, 4, 25, 10, 51, 0),
    )


def test_get_photo_valid_id(client, mock_photo):
    with patch("tagline_backend_app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.get(f"/photos/{mock_photo.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_photo.id)
        assert data["object_key"] == mock_photo.filename
        assert data["metadata"]["description"] == mock_photo.description
        assert "last_modified" in data


def test_get_photo_nonexistent_id(client):
    with patch("tagline_backend_app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = None
        fake_id = uuid.uuid4()
        response = client.get(f"/photos/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Photo not found"


def test_get_photo_invalid_uuid(client):
    response = client.get("/photos/not-a-uuid")
    assert response.status_code == 422
    assert "detail" in response.json()
