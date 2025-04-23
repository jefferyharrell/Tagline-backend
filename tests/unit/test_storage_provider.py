"""
Unit tests for the PhotoStorageProvider interface contract.
Ensures NotImplementedError is raised for upload/delete, and get_url returns None by default.
"""

import pytest

from app.storage.provider import PhotoStorageProvider


class DummyProvider(PhotoStorageProvider):
    def list(self, prefix=None):
        return []

    def retrieve(self, key):
        raise FileNotFoundError


def test_upload_and_delete_raise_not_implemented():
    provider = DummyProvider()
    import io

    with pytest.raises(NotImplementedError, match="upload"):
        provider.upload("foo.jpg", io.BytesIO(b"dummy"))
    with pytest.raises(NotImplementedError, match="deletion"):
        provider.delete("foo.jpg")


def test_get_url_default_returns_none():
    provider = DummyProvider()
    assert provider.get_url("foo.jpg") is None
