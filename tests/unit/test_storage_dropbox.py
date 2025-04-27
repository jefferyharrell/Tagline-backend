"""
Unit tests for DropboxStorageProvider
- Config/validation (credentials, root path)
- list (mock Dropbox SDK, returns expected)
- retrieve (mock Dropbox SDK, returns data or raises)
- Error handling (bad creds, file not found)
"""
import pytest
from unittest.mock import patch, Mock
from tagline_backend_app.storage.dropbox import DropboxStorageProvider, StorageProviderMisconfigured
from dropbox.exceptions import ApiError

pytestmark = pytest.mark.unit

# --- Fixtures and helpers ---
@pytest.fixture
def dropbox_creds():
    return dict(refresh_token="tok", app_key="key", app_secret="sec", root_path="/photos")

# --- Config/validation ---
def test_init_refresh_token_success(dropbox_creds):
    with patch("dropbox.Dropbox") as MockDbx:
        provider = DropboxStorageProvider(**dropbox_creds)
        MockDbx.assert_called_once_with(
            oauth2_refresh_token="tok", app_key="key", app_secret="sec"
        )
        assert provider.root_path == "/photos"

def test_init_access_token_success():
    with patch("dropbox.Dropbox") as MockDbx:
        provider = DropboxStorageProvider(access_token="abc", root_path="/foo")
        MockDbx.assert_called_once_with("abc")
        assert provider.root_path == "/foo"

def test_init_missing_creds_raises():
    with pytest.raises(StorageProviderMisconfigured):
        DropboxStorageProvider()

# --- list ---
def test_list_returns_expected(dropbox_creds):
    entries = [Mock(path_display="/photos/cat.jpg"), Mock(path_display="/photos/dog.jpg")]
    with patch("dropbox.Dropbox") as MockDbx:
        mock_dbx = MockDbx.return_value
        mock_res = Mock(entries=entries, has_more=False)
        mock_dbx.files_list_folder.return_value = mock_res
        provider = DropboxStorageProvider(**dropbox_creds)
        # Patch _process_entries to just return filenames
        with patch.object(provider, "_process_entries", return_value=["cat.jpg", "dog.jpg"]):
            result = provider.list()
            assert result == ["cat.jpg", "dog.jpg"]
            mock_dbx.files_list_folder.assert_called_once_with("/photos", recursive=True)

def test_list_handles_api_error(dropbox_creds):
    with patch("dropbox.Dropbox") as MockDbx:
        mock_dbx = MockDbx.return_value
        mock_dbx.files_list_folder.side_effect = ApiError("req", "err", "user", "en-US")
        provider = DropboxStorageProvider(**dropbox_creds)
        with pytest.raises(FileNotFoundError):
            provider.list()

# --- retrieve ---
def test_retrieve_success(dropbox_creds):
    with patch("dropbox.Dropbox") as MockDbx:
        mock_dbx = MockDbx.return_value
        mock_res = Mock(content=b"data")
        mock_dbx.files_download.return_value = (Mock(), mock_res)
        provider = DropboxStorageProvider(**dropbox_creds)
        result = provider.retrieve("cat.jpg")
        assert result.read() == b"data"
        mock_dbx.files_download.assert_called_once()

def test_retrieve_handles_api_error(dropbox_creds):
    with patch("dropbox.Dropbox") as MockDbx:
        mock_dbx = MockDbx.return_value
        mock_dbx.files_download.side_effect = ApiError("req", "err", "user", "en-US")
        provider = DropboxStorageProvider(**dropbox_creds)
        with pytest.raises(FileNotFoundError):
            provider.retrieve("cat.jpg")
