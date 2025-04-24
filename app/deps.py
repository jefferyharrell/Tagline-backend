"""
deps.py

Dependency injection helpers for FastAPI.
"""

from fastapi import Request


def get_token_store(request: Request):
    return request.app.state.token_store
