"""
Unit tests for tagline_backend_app.redis_token_store.RedisTokenStore
"""
import pytest
from unittest.mock import MagicMock
from tagline_backend_app.redis_token_store import RedisTokenStore

pytestmark = pytest.mark.unit

@pytest.fixture
def mock_redis():
    mock = MagicMock()
    # Default get returns None (token not found)
    mock.get.return_value = None
    mock.ttl.return_value = 100
    mock.pipeline.return_value = MagicMock(set=MagicMock(), execute=MagicMock())
    return mock

@pytest.fixture
def token_store(mock_redis):
    # Patch RedisTokenStore to use mock redis
    store = RedisTokenStore.__new__(RedisTokenStore)
    store.client = mock_redis
    return store

def test_store_refresh_token(token_store, mock_redis):
    token_store.store_refresh_token("tok123", 60)
    mock_redis.set.assert_called_once()
    args, kwargs = mock_redis.set.call_args
    assert args[0] == "tok123"
    assert kwargs["ex"] == 60

def test_is_refresh_token_valid_true(token_store, mock_redis):
    mock_redis.get.return_value = '{"revoked": false}'
    assert token_store.is_refresh_token_valid("tok123") is True

def test_is_refresh_token_valid_false_not_found(token_store, mock_redis):
    mock_redis.get.return_value = None
    assert token_store.is_refresh_token_valid("tok123") is False

def test_is_refresh_token_valid_false_revoked(token_store, mock_redis):
    mock_redis.get.return_value = '{"revoked": true}'
    assert token_store.is_refresh_token_valid("tok123") is False

def test_is_refresh_token_valid_false_invalid_json(token_store, mock_redis):
    mock_redis.get.return_value = 'not-json'
    assert token_store.is_refresh_token_valid("tok123") is False

def test_revoke_refresh_token_valid(token_store, mock_redis):
    # Simulate token present and not revoked
    mock_redis.get.return_value = '{"revoked": false}'
    mock_redis.ttl.return_value = 42
    pipe = mock_redis.pipeline.return_value
    token_store.revoke_refresh_token("tok123")
    pipe.set.assert_called_once()
    pipe.execute.assert_called_once()
    # Should set revoked to True in stored JSON
    args, kwargs = pipe.set.call_args
    assert args[0] == "tok123"
    assert kwargs["ex"] == 42
    assert '"revoked": true' in args[1]

def test_revoke_refresh_token_not_found(token_store, mock_redis):
    mock_redis.get.return_value = None
    token_store.revoke_refresh_token("tok123")
    # Should not call set or execute
    pipe = mock_redis.pipeline.return_value
    pipe.set.assert_not_called()
    pipe.execute.assert_not_called()

def test_get_refresh_token_metadata_valid(token_store, mock_redis):
    mock_redis.get.return_value = '{"revoked": false}'
    mock_redis.ttl.return_value = 99
    meta = token_store.get_refresh_token_metadata("tok123")
    assert meta["revoked"] is False
    assert meta["ttl"] == 99

def test_get_refresh_token_metadata_not_found(token_store, mock_redis):
    mock_redis.get.return_value = None
    assert token_store.get_refresh_token_metadata("tok123") is None

def test_get_refresh_token_metadata_invalid_json(token_store, mock_redis):
    mock_redis.get.return_value = 'not-json'
    assert token_store.get_refresh_token_metadata("tok123") is None
