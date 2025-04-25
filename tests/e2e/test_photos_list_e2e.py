"""
E2E test for GET /photos list endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.crud.photo import PhotoRepository
from app.db import get_db
from app.main import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    return TestClient(app)


def seed_photos(db, n):
    repo = PhotoRepository(db)
    for i in range(n):
        repo.create(filename=f"img_{i}.jpg", metadata={"description": f"desc {i}"})


def test_photos_list_e2e(client):
    # Seed the DB using the test client's app dependency
    db = next(client.app.dependency_overrides[get_db]())
    seed_photos(db, 7)
    response = client.get("/photos?limit=3&offset=4")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 7
    assert data["limit"] == 3
    assert data["offset"] == 4
    assert len(data["items"]) == 3
    for i, item in enumerate(data["items"]):
        assert "object_key" in item
        assert item["object_key"] == f"img_{i+4}.jpg"
        assert "metadata" in item
        assert item["metadata"]["description"] == f"desc {i+4}"
        assert "last_modified" in item
        assert isinstance(item["last_modified"], str)
