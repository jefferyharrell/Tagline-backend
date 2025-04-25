"""
Unit tests for PATCH /photos/{id}/metadata endpoint in Tagline backend.
Covers: valid update, empty description, missing/invalid fields, nonexistent photo, invalid UUID, and last_modified validation.
"""

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_photo():
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


def test_patch_photo_valid_update(client, mock_photo):
    with (
        patch("app.routes.root.PhotoRepository") as MockRepo,
        patch("sqlalchemy.orm.Session.commit"),
        patch("sqlalchemy.orm.Session.refresh"),
    ):
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={"metadata": {"description": "New desc"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["description"] == "New desc"


def test_patch_photo_empty_description(client, mock_photo):
    with (
        patch("app.routes.root.PhotoRepository") as MockRepo,
        patch("sqlalchemy.orm.Session.commit"),
        patch("sqlalchemy.orm.Session.refresh"),
    ):
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={"metadata": {"description": ""}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["description"] == ""


def test_patch_photo_missing_description(client, mock_photo):
    with patch("app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={"metadata": {}},
        )
        assert response.status_code == 422
        assert "description is required" in response.json()["detail"]


def test_patch_photo_nonstring_description(client, mock_photo):
    with patch("app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={"metadata": {"description": 123}},
        )
        assert response.status_code == 422
        assert "description is required" in response.json()["detail"]


def test_patch_photo_nonexistent_id(client):
    with patch("app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = None
        fake_id = uuid.uuid4()
        response = client.patch(
            f"/photos/{fake_id}/metadata",
            json={"metadata": {"description": "desc"}},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Photo not found"


def test_patch_photo_invalid_uuid(client):
    response = client.patch(
        "/photos/not-a-uuid/metadata", json={"metadata": {"description": "desc"}}
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_patch_photo_last_modified_valid(client, mock_photo):
    with (
        patch("app.routes.root.PhotoRepository") as MockRepo,
        patch("sqlalchemy.orm.Session.commit"),
        patch("sqlalchemy.orm.Session.refresh"),
    ):
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={
                "metadata": {
                    "description": "desc",
                    "last_modified": "2025-04-25T12:00:00+00:00",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["description"] == "desc"
        assert "last_modified" in data


def test_patch_photo_last_modified_invalid(client, mock_photo):
    with patch("app.routes.root.PhotoRepository") as MockRepo:
        instance = MockRepo.return_value
        instance.get.return_value = mock_photo
        response = client.patch(
            f"/photos/{mock_photo.id}/metadata",
            json={"metadata": {"description": "desc", "last_modified": "not-a-date"}},
        )
        assert response.status_code == 422
        assert (
            "last_modified must be RFC3339/ISO8601 string" in response.json()["detail"]
        )
