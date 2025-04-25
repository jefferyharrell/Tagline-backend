"""
Integration tests for GET /photos/{id}/image endpoint.
Uses in-memory SQLite and InMemoryStorageProvider.
"""

import io
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import get_db, get_engine, get_session_local
from app.main import create_app
from app.models import Base, Photo


@pytest.fixture(scope="function")
def app_with_memory_storage(monkeypatch):
    # Use a file-based SQLite DB for test isolation
    tmpfile = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_url = f"sqlite:///{tmpfile.name}"
    os.environ["DATABASE_URL"] = db_url
    os.environ["STORAGE_PROVIDER"] = "memory"

    # Bust caches to ensure fresh engine/session
    try:
        get_engine.cache_clear()
    except AttributeError:
        pass
    try:
        get_session_local.cache_clear()
    except AttributeError:
        pass

    # Create engine/session and schema
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    # Create app
    app = create_app()

    # Override get_db to always return db_session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Patch storage provider to always use InMemoryStorageProvider
    from app.storage.memory import InMemoryStorageProvider

    provider = InMemoryStorageProvider()
    app.state.get_photo_storage_provider = lambda app_: provider

    yield TestClient(app)


def test_get_photo_image_success(client, db_session):
    # Add a photo and image to storage
    photo = Photo(filename="cat.jpg", description="meow")
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)
    # Store image in InMemoryStorageProvider
    provider = client.app.state.get_photo_storage_provider(client.app)
    provider.upload("cat.jpg", io.BytesIO(b"cat image data"))
    resp = client.get(f"/photos/{photo.id}/image")
    assert resp.status_code == 200
    assert resp.content == b"cat image data"
    assert resp.headers["content-type"].startswith("image/")


def test_get_photo_image_photo_not_found(client, db_session):
    db_session.query(Photo).first()  # Touch db_session to trigger schema creation
    resp = client.get("/photos/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/image")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo not found"


def test_get_photo_image_file_not_found(client, db_session):
    photo = Photo(filename="ghost.jpg", description="boo")
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)
    resp = client.get(f"/photos/{photo.id}/image")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Photo file not found"
