import json
from unittest.mock import MagicMock, patch

import pytest

from tagline_backend_app.redis_token_store import RedisTokenStore


@pytest.fixture
def redis_url():
    return "redis://localhost:6379/0"


@pytest.fixture
def mock_redis():
    with patch(
        "tagline_backend_app.redis_token_store.redis.Redis.from_url"
    ) as mock_from_url:
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        yield mock_client


@pytest.fixture
def store(redis_url, mock_redis):
    return RedisTokenStore(redis_url)


def test_store_refresh_token_sets_token_with_ttl(store, mock_redis):
    store.store_refresh_token("token123", 3600)
    mock_redis.set.assert_called_once_with(
        "token123", json.dumps({"revoked": False}), ex=3600
    )


def test_is_refresh_token_valid_true(store, mock_redis):
    mock_redis.get.return_value = json.dumps({"revoked": False})
    assert store.is_refresh_token_valid("token123") is True


def test_is_refresh_token_valid_revoked(store, mock_redis):
    mock_redis.get.return_value = json.dumps({"revoked": True})
    assert store.is_refresh_token_valid("token123") is False


def test_is_refresh_token_valid_missing(store, mock_redis):
    mock_redis.get.return_value = None
    assert store.is_refresh_token_valid("missing") is False


def test_is_refresh_token_valid_bad_json(store, mock_redis):
    mock_redis.get.return_value = "not-json"
    assert store.is_refresh_token_valid("bad") is False


def test_revoke_refresh_token_marks_revoked_and_preserves_ttl(store, mock_redis):
    # Setup
    mock_redis.get.return_value = json.dumps({"revoked": False})
    mock_redis.ttl.return_value = 1234
    mock_pipe = MagicMock()
    mock_redis.pipeline.return_value = mock_pipe
    # Act
    store.revoke_refresh_token("token123")
    # Assert
    mock_pipe.set.assert_called_once_with(
        "token123", json.dumps({"revoked": True}), ex=1234
    )
    mock_pipe.execute.assert_called_once()


def test_revoke_refresh_token_missing_token(store, mock_redis):
    mock_redis.get.return_value = None
    store.revoke_refresh_token("missing")
    # Should not call set/execute
    mock_redis.pipeline.return_value.set.assert_not_called()
    mock_redis.pipeline.return_value.execute.assert_not_called()


def test_revoke_refresh_token_bad_json(store, mock_redis):
    mock_redis.get.return_value = "not-json"
    store.revoke_refresh_token("bad")
    mock_redis.pipeline.return_value.set.assert_not_called()
    mock_redis.pipeline.return_value.execute.assert_not_called()


def test_revoke_refresh_token_ttl_edge_case(store, mock_redis):
    mock_redis.get.return_value = json.dumps({"revoked": False})
    mock_redis.ttl.return_value = -2  # Expired or no TTL
    mock_pipe = MagicMock()
    mock_redis.pipeline.return_value = mock_pipe
    store.revoke_refresh_token("token123")
    mock_pipe.set.assert_called_once_with(
        "token123", json.dumps({"revoked": True}), ex=None
    )
    mock_pipe.execute.assert_called_once()


def test_get_refresh_token_metadata_valid(store, mock_redis):
    mock_redis.get.return_value = json.dumps({"revoked": False})
    mock_redis.ttl.return_value = 100
    result = store.get_refresh_token_metadata("token123")
    assert result["revoked"] is False
    assert result["ttl"] == 100


def test_get_refresh_token_metadata_missing(store, mock_redis):
    mock_redis.get.return_value = None
    assert store.get_refresh_token_metadata("missing") is None


def test_get_refresh_token_metadata_bad_json(store, mock_redis):
    mock_redis.get.return_value = "not-json"
    assert store.get_refresh_token_metadata("bad") is None


def test_get_refresh_token_metadata_ttl_non_int(store, mock_redis):
    mock_redis.get.return_value = json.dumps({"revoked": False})
    mock_redis.ttl.return_value = "not-an-int"
    result = store.get_refresh_token_metadata("token123")
    assert result["ttl"] is None
