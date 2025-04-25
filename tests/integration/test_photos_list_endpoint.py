"""
Unit tests for GET /photos list endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.crud.photo import PhotoRepository
from app.db import get_db
from app.main import create_app


@pytest.fixture
def test_app(tmp_path_factory):
    app = create_app()
    # Use a temp SQLite file DB
    tmp_path = tmp_path_factory.mktemp("db")
    db_url = f"sqlite:///{tmp_path}/test_photos.sqlite3"
    app.dependency_overrides[get_db] = lambda: next(_test_db_session(db_url))
    return app


def _test_db_session(db_url):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models import Base

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


def seed_photos(db, n):
    repo = PhotoRepository(db)
    for i in range(n):
        repo.create(filename=f"img_{i}.jpg", metadata={"description": f"desc {i}"})


def test_photos_list_happy_path(client):
    db = client.app.dependency_overrides[get_db]()
    seed_photos(db, 10)
    response = client.get("/photos?limit=5&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert data["limit"] == 5
    assert data["offset"] == 2
    assert len(data["items"]) == 5
    for i, item in enumerate(data["items"]):
        assert "object_key" in item
        assert item["object_key"] == f"img_{i+2}.jpg"
        assert "metadata" in item
        assert item["metadata"]["description"] == f"desc {i+2}"
        assert "last_modified" in item
        assert isinstance(item["last_modified"], str)


def test_photos_list_limit_validation(client):
    response = client.get("/photos?limit=0")
    assert response.status_code == 422
    response = client.get("/photos?limit=101")
    assert response.status_code == 422


def test_photos_list_offset_validation(client):
    response = client.get("/photos?offset=-1")
    assert response.status_code == 422


def test_photos_list_empty(client):
    response = client.get("/photos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
