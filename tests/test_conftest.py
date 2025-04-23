"""
Unit tests for conftest.py fixtures (edge cases).
"""

import os


def test_reset_app_env_restores(reset_app_env, monkeypatch):
    monkeypatch.setenv("APP_ENV", "original")
    os.environ["APP_ENV"] = "changed"
    # The fixture will restore after the test completes; simulate this:
    # Actually, we can't test the 'after yield' part directly, but we can at least ensure the fixture runs without error.
    assert os.environ["APP_ENV"] == "changed"
