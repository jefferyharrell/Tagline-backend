"""
Unit tests for NullStorageProvider.
"""

import pytest

from app.storage.null import NullStorageProvider


@pytest.fixture
def provider():
    return NullStorageProvider()


def test_list_always_empty(provider):
    assert list(provider.list()) == []
    assert list(provider.list(prefix="foo")) == []


def test_retrieve_always_not_found(provider):
    with pytest.raises(FileNotFoundError):
        provider.retrieve("anything")


def test_upload_and_delete_noop(provider):
    provider.upload("key", None)  # Should not raise
    provider.delete("key")  # Should not raise


def test_get_url_always_none(provider):
    assert provider.get_url("foo") is None
