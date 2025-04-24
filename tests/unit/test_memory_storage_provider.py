"""
Unit tests for InMemoryPhotoStorageProvider.
"""

from io import BytesIO

import pytest

from app.storage.memory import InMemoryPhotoStorageProvider


@pytest.fixture
def provider():
    return InMemoryPhotoStorageProvider()


def test_list_and_upload(provider):
    assert list(provider.list()) == []
    provider.upload("foo.jpg", BytesIO(b"imagebytes"))
    assert list(provider.list()) == ["foo.jpg"]
    assert list(provider.list(prefix="foo")) == ["foo.jpg"]
    assert list(provider.list(prefix="bar")) == []


def test_retrieve(provider):
    provider.upload("foo", BytesIO(b"abc"))
    f = provider.retrieve("foo")
    assert f.read() == b"abc"
    with pytest.raises(FileNotFoundError):
        provider.retrieve("nope")


def test_delete(provider):
    provider.upload("foo", BytesIO(b"abc"))
    provider.delete("foo")
    with pytest.raises(FileNotFoundError):
        provider.retrieve("foo")


def test_get_url(provider):
    provider.upload("foo", BytesIO(b"abc"))
    assert provider.get_url("foo") is None
