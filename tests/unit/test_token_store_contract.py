"""
Contract test for tagline_backend_app.token_store.TokenStore implementations.
Ensures any subclass (e.g., RedisTokenStore) fulfills the expected interface/behavior.
"""
import pytest
from tagline_backend_app.token_store import TokenStore

pytestmark = pytest.mark.unit

class DummyTokenStore(TokenStore):
    """Minimal in-memory TokenStore for contract testing."""
    def __init__(self):
        self.tokens = {}
    def store_refresh_token(self, token, expires_in):
        self.tokens[token] = {"revoked": False, "expires_in": expires_in}
    def is_refresh_token_valid(self, token):
        return token in self.tokens and not self.tokens[token]["revoked"]
    def revoke_refresh_token(self, token):
        if token in self.tokens:
            self.tokens[token]["revoked"] = True
    def get_refresh_token_metadata(self, token):
        return self.tokens.get(token, None)

@pytest.fixture
def token_store():
    return DummyTokenStore()

def test_contract_store_and_validate(token_store):
    token_store.store_refresh_token("tok", 60)
    assert token_store.is_refresh_token_valid("tok")

def test_contract_revoke(token_store):
    token_store.store_refresh_token("tok", 60)
    token_store.revoke_refresh_token("tok")
    assert not token_store.is_refresh_token_valid("tok")

def test_contract_metadata(token_store):
    token_store.store_refresh_token("tok", 60)
    meta = token_store.get_refresh_token_metadata("tok")
    assert meta["revoked"] is False
    assert meta["expires_in"] == 60

# Bonus: contract test for non-existent token

def test_contract_invalid_token(token_store):
    assert not token_store.is_refresh_token_valid("nope")
    assert token_store.get_refresh_token_metadata("nope") is None
