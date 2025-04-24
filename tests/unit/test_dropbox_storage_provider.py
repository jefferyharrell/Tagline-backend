"""
Unit tests for DropboxStorageProvider implementation.
Tests initialization, listing, and retrieval of files using mocked Dropbox API.
"""

from unittest.mock import MagicMock, patch

import pytest
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata

from app.storage.dropbox import DropboxStorageProvider
from app.storage.provider import StorageProviderMisconfigured


def test_dropbox_init_raises_when_misconfigured():
    # Test with no credentials
    with pytest.raises(
        StorageProviderMisconfigured, match="Missing Dropbox credentials"
    ):
        DropboxStorageProvider()

    # Test with incomplete refresh token credentials
    with pytest.raises(
        StorageProviderMisconfigured, match="Missing Dropbox credentials"
    ):
        DropboxStorageProvider(refresh_token="token-only")


@patch("dropbox.Dropbox")
def test_dropbox_init_with_refresh_token(mock_dropbox):
    # Test initialization with refresh token
    provider = DropboxStorageProvider(
        refresh_token="dummy-refresh-token",
        app_key="dummy-app-key",
        app_secret="dummy-app-secret",
        root_path="/test/path",
    )
    assert provider.root_path == "/test/path"
    mock_dropbox.assert_called_once()


@patch("dropbox.Dropbox")
def test_dropbox_init_with_access_token(mock_dropbox):
    # Test initialization with legacy access token
    provider = DropboxStorageProvider(
        access_token="dummy-access-token", root_path="/photos"
    )
    assert provider.root_path == "/photos"
    mock_dropbox.assert_called_once()


@patch("dropbox.Dropbox")
def test_dropbox_list(mock_dropbox):
    # Setup mock
    mock_dbx = mock_dropbox.return_value
    mock_result = MagicMock()

    # Create mock file entries
    file1 = MagicMock(spec=FileMetadata)
    file1.path_display = "/test/path/photo1.jpg"

    file2 = MagicMock(spec=FileMetadata)
    file2.path_display = "/test/path/subdir/photo2.jpg"

    folder = MagicMock()  # Not a FileMetadata
    folder.path_display = "/test/path/subdir"

    mock_result.entries = [file1, file2, folder]
    mock_dbx.files_list_folder.return_value = mock_result

    # Initialize with test root path
    provider = DropboxStorageProvider(
        refresh_token="dummy-refresh-token",
        app_key="dummy-app-key",
        app_secret="dummy-app-secret",
        root_path="/test/path",
    )

    # Test listing all files
    result = provider.list()
    assert sorted(result) == ["photo1.jpg", "subdir/photo2.jpg"]

    # Test listing with prefix
    result = provider.list(prefix="subdir/")
    assert result == ["subdir/photo2.jpg"]


@patch("dropbox.Dropbox")
def test_dropbox_retrieve(mock_dropbox):
    # Setup mock
    mock_dbx = mock_dropbox.return_value
    mock_metadata = MagicMock()
    mock_response = MagicMock()
    mock_response.content = b"test image data"

    mock_dbx.files_download.return_value = (mock_metadata, mock_response)

    # Initialize provider
    provider = DropboxStorageProvider(
        refresh_token="dummy-refresh-token",
        app_key="dummy-app-key",
        app_secret="dummy-app-secret",
        root_path="/test/path",
    )

    # Test retrieving a file
    result = provider.retrieve("photo.jpg")

    # Verify the result is a BytesIO with correct content
    assert result.read() == b"test image data"

    # Verify Dropbox API was called with correct path
    mock_dbx.files_download.assert_called_once_with("/test/path/photo.jpg")


@patch("dropbox.Dropbox")
def test_dropbox_api_errors(mock_dropbox):
    # Setup mock to raise ApiError with all required parameters
    mock_dbx = mock_dropbox.return_value

    # Create properly structured mock ApiErrors
    api_error = ApiError(
        error=MagicMock(),  # The actual error object
        user_message_text="User-facing error",
        user_message_locale="en",
        request_id="mock-request-id",  # Required by Pyright
    )

    mock_dbx.files_list_folder.side_effect = api_error
    mock_dbx.files_download.side_effect = api_error

    # Initialize provider
    provider = DropboxStorageProvider(
        refresh_token="dummy-refresh-token",
        app_key="dummy-app-key",
        app_secret="dummy-app-secret",
    )

    # Test list() raises FileNotFoundError when API fails
    with pytest.raises(FileNotFoundError, match="Dropbox listing failed"):
        provider.list()

    # Test retrieve() raises FileNotFoundError when API fails
    with pytest.raises(FileNotFoundError, match="Dropbox file not found"):
        provider.retrieve("missing.jpg")
