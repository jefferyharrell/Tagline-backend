"""
Unit tests for DropboxPhotoStorageProvider stub.
Ensures all methods raise NotImplementedError as expected.
"""

import pytest

from app.storage.dropbox import DropboxPhotoStorageProvider


def test_dropbox_init_raises():
    with pytest.raises(NotImplementedError, match="not implemented"):
        DropboxPhotoStorageProvider(access_token="dummy-token")


def test_dropbox_list_raises():
    class Dummy(DropboxPhotoStorageProvider):
        def __init__(self):
            pass  # Bypass __init__

    provider = Dummy()
    with pytest.raises(NotImplementedError, match="not implemented"):
        provider.list()


def test_dropbox_retrieve_raises():
    class Dummy(DropboxPhotoStorageProvider):
        def __init__(self):
            pass

    provider = Dummy()
    with pytest.raises(NotImplementedError, match="not implemented"):
        provider.retrieve("foo.jpg")
