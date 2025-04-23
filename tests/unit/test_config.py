"""
Unit tests for app.config (Settings).
"""

from app.config import get_settings


def test_settings_defaults(ensure_filesystem_path_set, monkeypatch):
    # Use the new fixture that only sets the path, not the DB
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()  # Clear cache after monkeypatch
    s = get_settings()
    assert s.DATABASE_URL == "sqlite:///./tagline.db"


def test_settings_env_override(monkeypatch, ensure_filesystem_path_set):
    # Use the new fixture that only sets the path, not the DB
    test_db_url = "postgresql://user:password@host:port/dbname"
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    get_settings.cache_clear()  # Clear cache after monkeypatch
    s = get_settings()
    assert s.DATABASE_URL == test_db_url
