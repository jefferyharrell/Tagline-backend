"""
Unit tests for app.config (Settings).
"""

from app import config


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    s = config.Settings()
    assert s.DATABASE_URL == "sqlite:///./tagline.db"


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    s = config.Settings()
    assert s.DATABASE_URL == "postgresql://user:pass@localhost/db"
