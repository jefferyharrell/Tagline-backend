"""
Unit tests for tagline_backend_app.deps
Covers: get_token_store, get_current_user (mocking FastAPI request/app, AuthService, token validation)
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from tagline_backend_app.deps import get_current_user, get_token_store

pytestmark = pytest.mark.unit


def make_request_with_token_store(token_store):
    app = Mock()
    app.state.token_store = token_store
    request = Mock()
    request.app = app
    return request


def test_get_token_store_returns_from_app_state():
    token_store = object()
    request = make_request_with_token_store(token_store)
    assert get_token_store(request) is token_store


@patch("tagline_backend_app.deps.AuthService")
def test_get_current_user_valid_token(MockAuthService):
    mock_service = MockAuthService.return_value
    mock_service.validate_token.return_value = {"sub": "user"}
    request = make_request_with_token_store(Mock())
    result = get_current_user(request, access_token="goodtoken")
    assert result == {"sub": "user"}
    mock_service.validate_token.assert_called_once_with(
        "goodtoken", token_type="access"
    )


@patch("tagline_backend_app.deps.AuthService")
def test_get_current_user_missing_token(MockAuthService):
    request = make_request_with_token_store(Mock())
    with pytest.raises(HTTPException) as exc:
        get_current_user(request, access_token=None)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing authentication token" in str(exc.value.detail)


@patch("tagline_backend_app.deps.AuthService")
def test_get_current_user_invalid_token(MockAuthService):
    mock_service = MockAuthService.return_value
    mock_service.validate_token.return_value = None
    request = make_request_with_token_store(Mock())
    with pytest.raises(HTTPException) as exc:
        get_current_user(request, access_token="badtoken")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid or expired token" in str(exc.value.detail)
