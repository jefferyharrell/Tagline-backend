"""
Unit tests for NullStorageProvider
- All ops: always no-op or fail gracefully (list, retrieve, delete)
"""
import pytest
from tagline_backend_app.storage.null import NullStorageProvider

pytestmark = pytest.mark.unit

def test_list_always_empty():
    provider = NullStorageProvider()
    assert list(provider.list()) == []
    assert list(provider.list(prefix="foo")) == []

def test_retrieve_always_raises():
    provider = NullStorageProvider()
    with pytest.raises(FileNotFoundError):
        provider.retrieve("foo.jpg")

def test_upload_noop():
    provider = NullStorageProvider()
    provider.upload("foo.jpg", None)  # Should not raise

def test_delete_noop():
    provider = NullStorageProvider()
    provider.delete("foo.jpg")  # Should not raise

def test_get_url_always_none():
    provider = NullStorageProvider()
    assert provider.get_url("foo.jpg") is None
