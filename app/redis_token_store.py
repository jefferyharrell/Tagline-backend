"""
redis_token_store.py

Redis-backed implementation of TokenStore for refresh token storage.
"""

import json
from typing import Optional

import redis

from app.token_store import TokenStore


class RedisTokenStore(TokenStore):
    def __init__(self, redis_url: str):
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def store_refresh_token(self, token: str, expires_in: int) -> None:
        # Store the token as a key with a TTL; value is simple metadata (JSON)
        data = json.dumps({"revoked": False})
        self.client.set(token, data, ex=expires_in)

    def is_refresh_token_valid(self, token: str) -> bool:
        val = self.client.get(token)
        if not isinstance(val, str):
            return False
        try:
            data = json.loads(val)
        except Exception:
            return False
        return not data.get("revoked", False)

    def revoke_refresh_token(self, token: str) -> None:
        pipe = self.client.pipeline()
        val = self.client.get(token)
        if not isinstance(val, str):
            return  # Already gone or expired
        try:
            data = json.loads(val)
        except Exception:
            return
        data["revoked"] = True
        # Overwrite the value, preserve TTL
        ttl_val = self.client.ttl(token)
        ttl = ttl_val if isinstance(ttl_val, int) and ttl_val > 0 else None
        pipe.set(token, json.dumps(data), ex=ttl)
        pipe.execute()

    def get_refresh_token_metadata(self, token: str) -> Optional[dict]:
        val = self.client.get(token)
        if not isinstance(val, str):
            return None
        try:
            data = json.loads(val)
        except Exception:
            return None
        ttl_val = self.client.ttl(token)
        ttl = ttl_val if isinstance(ttl_val, int) else None
        data["ttl"] = ttl
        return data
