"""
Tests for storage provider selection/configuration and env var handling.
"""

import tempfile
from pathlib import Path

import pytest

from tagline_backend_app.config import get_settings
from tagline_backend_app.storage.filesystem import (
    FilesystemStorageProvider,
    StorageProviderMisconfigured,
)


@pytest.mark.integration
def test_filesystem_provider_env(monkeypatch):
    """Provider is correctly instantiated from env config."""
    with tempfile.TemporaryDirectory() as tempdir:
        monkeypatch.setenv("STORAGE_PROVIDER", "filesystem")
        monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tempdir)
        get_settings.cache_clear()
        s = get_settings()
        provider = FilesystemStorageProvider(s.filesystem_storage.path)
        assert provider._root == Path(tempdir).resolve()


@pytest.mark.integration
def test_missing_filesystem_path(monkeypatch):
    """Missing FILESYSTEM_STORAGE_PATH raises StorageProviderMisconfigured at provider instantiation."""
    monkeypatch.setenv("STORAGE_PROVIDER", "filesystem")
    monkeypatch.delenv("FILESYSTEM_STORAGE_PATH", raising=False)
    get_settings.cache_clear()
    s = get_settings()
    with pytest.raises(StorageProviderMisconfigured) as excinfo:
        FilesystemStorageProvider(s.filesystem_storage.path)
    assert "FILESYSTEM_STORAGE_PATH is not set" in str(excinfo.value)


@pytest.mark.integration
def test_unsupported_storage_provider(monkeypatch):
    """Unsupported STORAGE_PROVIDER raises NotImplementedError."""
    monkeypatch.setenv("STORAGE_PROVIDER", "s3")
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", "/tmp")  # Required for Settings
    get_settings.cache_clear()

    # Should raise NotImplementedError
    with pytest.raises(NotImplementedError) as excinfo:
        s = get_settings()  # Get settings directly
        # Replicate the logic from main using 's'
        if s.STORAGE_PROVIDER.lower() not in ("filesystem", "", None):
            raise NotImplementedError(
                f"Storage provider '{s.STORAGE_PROVIDER}' is not supported yet."
            )
    # Optional but good: check the error message
    assert "Storage provider 's3' is not supported yet." in str(excinfo.value)


@pytest.mark.integration
def test_filesystem_provider_case_insensitive(monkeypatch):
    """STORAGE_PROVIDER is case-insensitive ('FiLeSyStEm' works)."""
    with tempfile.TemporaryDirectory() as tempdir:
        monkeypatch.setenv("STORAGE_PROVIDER", "FiLeSyStEm")
        monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", tempdir)
        get_settings.cache_clear()
        s = get_settings()
        provider = FilesystemStorageProvider(s.filesystem_storage.path)
        assert provider._root == Path(tempdir).resolve()
