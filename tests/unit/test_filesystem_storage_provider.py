"""
Unit tests for FilesystemPhotoStorageProvider.
Covers edge cases and security for list and retrieve.
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from app.storage.filesystem import FilesystemPhotoStorageProvider


@pytest.fixture
def temp_photo_dir():
    d = tempfile.mkdtemp()
    try:
        # Create some files and subdirs
        os.makedirs(os.path.join(d, "sub"), exist_ok=True)
        with open(os.path.join(d, "foo.jpg"), "wb") as f:
            f.write(b"foo")
        with open(os.path.join(d, "bar.png"), "wb") as f:
            f.write(b"bar")
        with open(os.path.join(d, "sub", "baz.gif"), "wb") as f:
            f.write(b"baz")
        yield Path(d)
    finally:
        shutil.rmtree(d)


def test_init_accepts_valid_dir(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    assert provider._root == temp_photo_dir.resolve()


def test_init_rejects_nonexistent():
    with pytest.raises(ValueError):
        FilesystemPhotoStorageProvider(Path("/no/such/dir"))


def test_init_rejects_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hi")
    with pytest.raises(ValueError):
        FilesystemPhotoStorageProvider(file)


def test_list_all_keys(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    keys = sorted(provider.list())
    assert keys == ["bar.png", "foo.jpg", str(Path("sub") / "baz.gif")]


def test_list_with_prefix(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    keys = list(provider.list("foo"))
    assert keys == ["foo.jpg"]
    keys = list(provider.list("sub/"))
    assert keys == [str(Path("sub") / "baz.gif")]


def test_retrieve_returns_file(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    with provider.retrieve("foo.jpg") as f:
        assert f.read() == b"foo"
    with provider.retrieve(str(Path("sub") / "baz.gif")) as f:
        assert f.read() == b"baz"


def test_retrieve_missing_raises(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    with pytest.raises(FileNotFoundError):
        provider.retrieve("nope.jpg")


def test_retrieve_traversal_raises(temp_photo_dir):
    provider = FilesystemPhotoStorageProvider(temp_photo_dir)
    # Attempt to escape root with ..
    with pytest.raises(FileNotFoundError):
        provider.retrieve("../foo.jpg")
    with pytest.raises(FileNotFoundError):
        provider.retrieve("sub/../../foo.jpg")
