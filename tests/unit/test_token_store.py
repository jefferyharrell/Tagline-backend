"""
Unit tests for the TokenStore ABC and (eventually) the RedisTokenStore implementation.
"""

import pytest

from tagline_backend_app.token_store import TokenStore


class DummyTokenStore(TokenStore):
    """Minimal concrete implementation for ABC testing only."""

    def store_refresh_token(self, token: str, expires_in: int) -> None:
        self._store = getattr(self, "_store", {})
        self._store[token] = {"expires_in": expires_in, "revoked": False}

    def is_refresh_token_valid(self, token: str) -> bool:
        data = getattr(self, "_store", {}).get(token)
        return bool(data and not data["revoked"])

    def revoke_refresh_token(self, token: str) -> None:
        store = getattr(self, "_store", {})
        if token in store:
            store[token]["revoked"] = True

    def get_refresh_token_metadata(self, token: str):
        return getattr(self, "_store", {}).get(token)


def test_token_store_abc_instantiation():
    with pytest.raises(TypeError):
        TokenStore()  # type: ignore  # Abstract class cannot be instantiated


def test_dummy_store_and_validate():
    store = DummyTokenStore()
    store.store_refresh_token("foo", 60)
    assert store.is_refresh_token_valid("foo")
    meta = store.get_refresh_token_metadata("foo")
    assert meta is not None
    assert meta["expires_in"] == 60


def test_dummy_revoke():
    store = DummyTokenStore()
    store.store_refresh_token("bar", 60)
    store.revoke_refresh_token("bar")
    assert not store.is_refresh_token_valid("bar")
    meta = store.get_refresh_token_metadata("bar")
    assert meta is not None
    assert meta["revoked"] is True


def test_dummy_missing_token():
    store = DummyTokenStore()
    assert not store.is_refresh_token_valid("baz")
    assert store.get_refresh_token_metadata("baz") is None
