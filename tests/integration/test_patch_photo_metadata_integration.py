"""
Integration tests for PATCH /photos/{id}/metadata endpoint.
Uses in-memory SQLite and InMemoryStorageProvider.
"""

import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from app.db import get_db
from app.main import create_app
from app.models import Base, Photo


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    clear_mappers()
    engine.dispose()


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "memory")
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


@pytest.fixture(scope="function")
def photo(db_session):
    photo = Photo(
        id=uuid.uuid4(),
        object_key="dog.jpg",
        description="A dog",
        updated_at=datetime(2025, 4, 25, 10, 51, 0),
    )
    db_session.add(photo)
    db_session.commit()
    return photo


def test_patch_photo_valid_update(client, db_session, photo):
    new_desc = "New desc"
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {"description": new_desc}},
    )
    assert response.status_code == 200
    db_session.refresh(photo)
    assert photo.description == new_desc
    # Confirm via GET
    get_resp = client.get(f"/photos/{photo.id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["metadata"]["description"] == new_desc


def test_patch_photo_empty_description(client, db_session, photo):
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {"description": ""}},
    )
    assert response.status_code == 200
    db_session.refresh(photo)
    assert photo.description == ""


def test_patch_photo_missing_description(client, photo):
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {}},
    )
    assert response.status_code == 422
    assert "description is required" in response.json()["detail"]


def test_patch_photo_nonstring_description(client, photo):
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {"description": 123}},
    )
    assert response.status_code == 422
    assert "description is required" in response.json()["detail"]


def test_patch_photo_last_modified_valid(client, db_session, photo):
    new_time = "2025-04-25T12:00:00+00:00"
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {"description": "desc", "last_modified": new_time}},
    )
    assert response.status_code == 200
    db_session.refresh(photo)
    # Optionally check updated_at if your model supports it


def test_patch_photo_last_modified_invalid(client, photo):
    response = client.patch(
        f"/photos/{photo.id}/metadata",
        json={"metadata": {"description": "desc", "last_modified": "not-a-date"}},
    )
    assert response.status_code == 422
    assert "last_modified must be RFC3339/ISO8601 string" in response.json()["detail"]


def test_patch_photo_nonexistent_id(client):
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
