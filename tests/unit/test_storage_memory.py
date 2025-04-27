"""
Unit tests for InMemoryStorageProvider
- All ops: behaves as ephemeral store (list, retrieve, add, delete)
"""

from io import BytesIO

import pytest

from tagline_backend_app.storage.memory import InMemoryStorageProvider

pytestmark = pytest.mark.unit


def test_upload_and_retrieve():
    provider = InMemoryStorageProvider()
    provider.upload("foo.jpg", BytesIO(b"cat"))
    result = provider.retrieve("foo.jpg")
    assert result.read() == b"cat"


def test_list_returns_keys():
    provider = InMemoryStorageProvider()
    provider.upload("cat.jpg", BytesIO(b"cat"))
    provider.upload("dog.jpg", BytesIO(b"dog"))
    assert set(provider.list()) == {"cat.jpg", "dog.jpg"}
    assert list(provider.list(prefix="cat")) == ["cat.jpg"]


def test_retrieve_missing_raises():
    provider = InMemoryStorageProvider()
    with pytest.raises(FileNotFoundError):
        provider.retrieve("nope.jpg")


def test_delete_removes_key():
    provider = InMemoryStorageProvider()
    provider.upload("cat.jpg", BytesIO(b"cat"))
    provider.delete("cat.jpg")
    with pytest.raises(FileNotFoundError):
        provider.retrieve("cat.jpg")


def test_get_url_always_none():
    provider = InMemoryStorageProvider()
    provider.upload("foo.jpg", BytesIO(b"cat"))
    assert provider.get_url("foo.jpg") is None
