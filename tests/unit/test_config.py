"""
Unit tests for tagline_backend_app.config (Settings, FilesystemProviderSettings, get_settings)
"""

import pytest

from tagline_backend_app.config import (
    FilesystemProviderSettings,
    Settings,
    get_settings,
)

pytestmark = pytest.mark.unit


def test_settings_env_loading(monkeypatch):
    # Patch Settings to ignore .env file
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    s = Settings()
    assert s.APP_ENV == "production"


def test_settings_defaults(monkeypatch):
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    s = Settings()
    # Defaults from class
    assert s.CORS_ALLOWED_ORIGINS == ""
    assert s.STORAGE_PROVIDER == "filesystem"


def test_settings_test_overrides(monkeypatch):
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    s = Settings()
    assert s.DATABASE_URL == "sqlite:///:memory:"


def test_filesystem_provider_settings_env(monkeypatch):
    monkeypatch.setenv("FILESYSTEM_STORAGE_PATH", "/tmp/photos")
    fs = FilesystemProviderSettings()
    assert str(fs.path) == "/tmp/photos"


def test_filesystem_provider_settings_default():
    fs = FilesystemProviderSettings()
    assert fs.path is None


def test_get_settings_cached(monkeypatch):
    # Clear lru_cache
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
    assert isinstance(s1, Settings)
