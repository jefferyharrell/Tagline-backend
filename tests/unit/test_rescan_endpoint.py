"""
Unit tests for the /rescan endpoint (app/routes/root.py)
Focus: Mock storage provider and DB repo to isolate endpoint logic.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def test_app():
    app = create_app()
    # Patch out the storage provider getter on app.state
    app.state.get_photo_storage_provider = MagicMock()
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


# Helper: Patch PhotoRepository in the endpoint module
@pytest.fixture
def mock_photo_repo():
    with patch("app.routes.root.PhotoRepository") as repo_cls:
        yield repo_cls


# Helper: Patch provider (returned by get_photo_storage_provider)
@pytest.fixture
def mock_provider(test_app):
    provider = MagicMock()
    test_app.state.get_photo_storage_provider.return_value = provider
    return provider


# Example happy path test
def test_rescan_happy_path(client, mock_photo_repo, mock_provider):
    # Arrange: provider returns two files, repo.list() returns one (already imported)
    mock_provider.list.return_value = ["foo.jpg", "bar.jpg"]
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = [MagicMock(filename="foo.jpg")]
    repo_instance.create.side_effect = lambda filename: MagicMock(filename=filename)

    # Act
    response = client.post("/rescan")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == ["bar.jpg"]
    assert data["imported_count"] == 1
    repo_instance.create.assert_called_once_with(filename="bar.jpg")
    mock_provider.list.assert_called_once()
    repo_instance.list.assert_called_once()


# No new files to import
def test_rescan_no_new_files(client, mock_photo_repo, mock_provider):
    mock_provider.list.return_value = ["foo.jpg"]
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = [MagicMock(filename="foo.jpg")]

    response = client.post("/rescan")
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == []
    assert data["imported_count"] == 0
    repo_instance.create.assert_not_called()


# Empty storage
def test_rescan_empty_storage(client, mock_photo_repo, mock_provider):
    mock_provider.list.return_value = []
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = []

    response = client.post("/rescan")
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == []
    assert data["imported_count"] == 0
    repo_instance.create.assert_not_called()


# Storage provider failure
def test_rescan_storage_provider_failure(client, mock_photo_repo, mock_provider):
    mock_provider.list.side_effect = Exception("storage fail")
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = []

    response = client.post("/rescan")
    assert response.status_code == 500
    assert "storage fail" in response.json()["detail"]


# DB failure on create
def test_rescan_db_failure_on_create(client, mock_photo_repo, mock_provider):
    mock_provider.list.return_value = ["foo.jpg"]
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = []
    repo_instance.create.side_effect = Exception("db fail")

    response = client.post("/rescan")
    assert response.status_code == 500
    assert "db fail" in response.json()["detail"]


# Large number of files
def test_rescan_large_number_of_files(client, mock_photo_repo, mock_provider):
    storage_files = [f"img_{i}.jpg" for i in range(100)]
    db_files = [MagicMock(filename=f"img_{i}.jpg") for i in range(50)]
    mock_provider.list.return_value = storage_files
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = db_files
    repo_instance.create.side_effect = lambda filename: MagicMock(filename=filename)

    response = client.post("/rescan")
    assert response.status_code == 200
    data = response.json()
    expected = [f"img_{i}.jpg" for i in range(50, 100)]
    assert sorted(data["imported"]) == expected
    assert data["imported_count"] == 50
    assert repo_instance.create.call_count == 50


# Non-ASCII filenames
def test_rescan_non_ascii_filenames(client, mock_photo_repo, mock_provider):
    mock_provider.list.return_value = ["café.jpg", "smile😊.png"]
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = []
    repo_instance.create.side_effect = lambda filename: MagicMock(filename=filename)

    response = client.post("/rescan")
    assert response.status_code == 200
    data = response.json()
    assert set(data["imported"]) == {"café.jpg", "smile😊.png"}
    assert data["imported_count"] == 2


# Malformed storage data (non-string values)
def test_rescan_malformed_storage_data(client, mock_photo_repo, mock_provider):
    mock_provider.list.return_value = [None, 123, "good.jpg"]
    repo_instance = mock_photo_repo.return_value
    repo_instance.list.return_value = []
    repo_instance.create.side_effect = lambda filename: MagicMock(filename=filename)

    response = client.post("/rescan")
    # Depending on implementation, this may error or skip bad values
    if response.status_code == 200:
        data = response.json()
        assert data["imported"] == ["good.jpg"]
        assert data["imported_count"] == 1
    else:
        # Accept 500 if implementation errors on bad input
        assert response.status_code == 500
