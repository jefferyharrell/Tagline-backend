"""
Integration test for the /rescan endpoint using:
- In-memory SQLite DB
- InMemoryStorageProvider
- Real FastAPI app stack (no mocks)

Marked with @pytest.mark.integration for easy selection.
"""

import os

import pytest
from fastapi.testclient import TestClient

from tagline_backend_app.config import get_settings
from tagline_backend_app.db import get_engine
from tagline_backend_app.main import create_app
from tagline_backend_app.models import Base
from tagline_backend_app.storage.memory import InMemoryStorageProvider


@pytest.fixture
def integration_app(tmp_path_factory):
    # Set up in-memory SQLite and memory storage provider
    os.environ["APP_ENV"] = "test"
    tmp_path = tmp_path_factory.mktemp("db")
    db_url = f"sqlite:///{tmp_path}/test_db.sqlite3"
    os.environ["DATABASE_URL"] = db_url
    os.environ["STORAGE_PROVIDER"] = "memory"
    get_settings.cache_clear()
    from sqlalchemy.orm import sessionmaker

    from tagline_backend_app.db import get_session_local

    # Bust the lru_cache so we get a fresh engine/sessionmaker
    get_engine.cache_clear()
    get_session_local.cache_clear()

    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    # Patch both get_engine and get_session_local globally (for extra safety)
    import tagline_backend_app.db as app_db

    app_db.get_engine = lambda: engine
    app_db.get_session_local = lambda: SessionLocal

    app = create_app()

    # Patch FastAPI dependencies as well
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session_local] = override_get_db

    # Inject a real memory provider into app state (for direct manipulation)
    provider = InMemoryStorageProvider()
    app.state.get_photo_storage_provider = lambda app: provider
    return app, provider


@pytest.fixture
def integration_client(integration_app):
    app, provider = integration_app
    return TestClient(app), provider


@pytest.mark.integration
def test_rescan_integration_happy_path(integration_client):
    client, provider = integration_client
    # Seed memory provider with files
    provider._store = {k: b"dummy" for k in ("a.jpg", "b.jpg", "c.jpg")}
    # DB starts empty
    response = client.post("/rescan")
    if response.status_code != 200:
        print(f"RESPONSE BODY: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert set(data["imported"]) == {"a.jpg", "b.jpg", "c.jpg"}
    assert data["imported_count"] == 3

    # Call again: should import nothing new
    response2 = client.post("/rescan")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["imported"] == []
    assert data2["imported_count"] == 0

    # Add a new file
    provider._store["d.jpg"] = b"dummy"
    response3 = client.post("/rescan")
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["imported"] == ["d.jpg"]
    assert data3["imported_count"] == 1
