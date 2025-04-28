"""
Unit tests for tagline_backend_app.auth_service.AuthService
"""

import pytest
from jose import jwt

from tagline_backend_app.auth_service import AuthService
from tagline_backend_app.config import Settings

pytestmark = pytest.mark.unit


# Minimal settings for testing
class DummyTokenStore:
    def __init__(self):
        self.stored = set()
        self.revoked = set()

    def is_refresh_token_valid(self, token):
        return token in self.stored and token not in self.revoked

    def store_refresh_token(self, token, expires_in):
        self.stored.add(token)

    def revoke_refresh_token(self, token):
        self.revoked.add(token)


@pytest.fixture
def settings():
    return Settings(
        BACKEND_PASSWORD="hunter2",
        JWT_SECRET_KEY="supersecret",
        ACCESS_TOKEN_EXPIRE_SECONDS=60,
        REFRESH_TOKEN_EXPIRE_SECONDS=120,
    )


@pytest.fixture
def token_store():
    instance = DummyTokenStore()
    return instance


@pytest.fixture
def auth_service(settings, token_store):
    return AuthService(settings, token_store)


def test_verify_password_correct(auth_service):
    assert auth_service.verify_password("hunter2") is True


def test_verify_password_incorrect(auth_service):
    assert auth_service.verify_password("wrong") is False


def test_issue_tokens(auth_service, token_store, settings):
    access, refresh, access_exp, refresh_exp = auth_service.issue_tokens()
    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert access_exp == settings.ACCESS_TOKEN_EXPIRE_SECONDS
    assert refresh_exp == settings.REFRESH_TOKEN_EXPIRE_SECONDS
    # Should be valid in store
    assert token_store.is_refresh_token_valid(refresh)
    # Access token should decode and have correct type
    payload = jwt.decode(access, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert payload["type"] == "access"
    payload_r = jwt.decode(refresh, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert payload_r["type"] == "refresh"


def test_refresh_tokens_success(auth_service, token_store, settings, monkeypatch):
    # Issue a refresh token
    _, refresh, _, _ = auth_service.issue_tokens()
    # Patch validate_token to return dummy claims
    monkeypatch.setattr(
        auth_service, "validate_token", lambda token, token_type: {"type": "refresh"}
    )
    # Patch revoke_refresh_token to just mark revoked
    monkeypatch.setattr(
        auth_service,
        "revoke_refresh_token",
        lambda token: token_store.revoke_refresh_token(token),
    )
    # Now refresh
    access2, refresh2, _, _ = auth_service.refresh_tokens(refresh)
    assert isinstance(access2, str)
    assert isinstance(refresh2, str)
    assert refresh2 != refresh
    # Old token should now be revoked
    assert refresh in token_store.revoked


def test_refresh_tokens_invalid(auth_service, monkeypatch):
    monkeypatch.setattr(auth_service, "validate_token", lambda token, token_type: None)
    with pytest.raises(Exception):
        auth_service.refresh_tokens("notavalidtoken")


def test_validate_token_access(auth_service, settings):
    access, _, _, _ = auth_service.issue_tokens()
    claims = auth_service.validate_token(access, token_type="access")
    assert claims is not None
    assert claims["type"] == "access"


def test_validate_token_refresh_and_revoked(auth_service, token_store, settings):
    _, refresh, _, _ = auth_service.issue_tokens()
    # Should be valid
    assert auth_service.validate_token(refresh, token_type="refresh") is not None
    # Revoke
    token_store.revoke_refresh_token(refresh)
    # Should now be invalid
    assert auth_service.validate_token(refresh, token_type="refresh") is None


def test_revoke_refresh_token_calls_store(auth_service, token_store):
    _, refresh, _, _ = auth_service.issue_tokens()
    auth_service.revoke_refresh_token(refresh)
    assert refresh in token_store.revoked
