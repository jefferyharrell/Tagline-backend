"""
Unit tests for FilesystemStorageProvider
- Config/validation (path handling, sandboxing)
- list (returns correct files, respects prefix)
- retrieve (returns file data, raises on not found)
- Error handling (bad path, traversal, etc)
"""

import os
from pathlib import Path

import pytest

from tagline_backend_app.storage.filesystem import (
    FilesystemStorageProvider,
    StorageProviderMisconfigured,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def tmp_storage_root(tmp_path):
    # Create a temp directory with some files
    d = tmp_path / "photos"
    d.mkdir()
    (d / "cat.jpg").write_bytes(b"meow")
    (d / "dog.jpg").write_bytes(b"woof")
    (d / "subdir").mkdir()
    (d / "subdir" / "bird.jpg").write_bytes(b"tweet")
    return d


def test_init_valid(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    assert provider._root == tmp_storage_root.resolve()


def test_init_invalid_none():
    with pytest.raises(StorageProviderMisconfigured):
        FilesystemStorageProvider(None)


def test_init_invalid_path():
    with pytest.raises(StorageProviderMisconfigured):
        FilesystemStorageProvider(Path("/does/not/exist"))


def test_list_files(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    files = set(provider.list())
    assert files == {"cat.jpg", "dog.jpg", os.path.join("subdir", "bird.jpg")}


def test_list_prefix(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    files = set(provider.list(prefix="subdir/"))
    assert files == {os.path.join("subdir", "bird.jpg")}


def test_retrieve_file(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    f = provider.retrieve("cat.jpg")
    assert f.read() == b"meow"
    f.close()


def test_retrieve_not_found(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    with pytest.raises(FileNotFoundError):
        provider.retrieve("nope.jpg")


def test_retrieve_path_traversal(tmp_storage_root):
    provider = FilesystemStorageProvider(tmp_storage_root)
    # Attempt to escape root
    with pytest.raises(FileNotFoundError):
        provider.retrieve("../cat.jpg")
