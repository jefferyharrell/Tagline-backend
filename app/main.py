from fastapi import FastAPI

from .config import get_settings
from .constants import APP_NAME
from .redis_token_store import RedisTokenStore
from .storage.filesystem import FilesystemPhotoStorageProvider


def create_app() -> FastAPI:
    settings = get_settings()
    # Fail fast if JWT_SECRET_KEY is not set (except in test)
    if not settings.JWT_SECRET_KEY and settings.APP_ENV.lower() != "test":
        raise RuntimeError(
            "JWT_SECRET_KEY must be set in environment/config for security!"
        )
    if not settings.REDIS_URL and settings.APP_ENV.lower() != "test":
        raise RuntimeError(
            "REDIS_URL must be set in environment/config for token storage!"
        )
    app = FastAPI(title=APP_NAME, version="0.1.0")
    # Storage provider selection logic
    if settings.STORAGE_PROVIDER.lower() in ("filesystem", "", None):
        app.state.photo_storage_provider = FilesystemPhotoStorageProvider(
            settings.filesystem_storage.path
        )
    elif settings.STORAGE_PROVIDER.lower() == "dropbox":
        raise NotImplementedError(
            "DropboxPhotoStorageProvider is not implemented yet. "
            "Set STORAGE_PROVIDER=filesystem or implement Dropbox support."
        )
    else:
        raise NotImplementedError(
            f"Storage provider '{settings.STORAGE_PROVIDER}' is not supported yet."
        )
    # Wire up RedisTokenStore
    app.state.token_store = RedisTokenStore(
        settings.REDIS_URL or "redis://localhost:6379/0"
    )
    # Register routes dynamically (reload to pick up changes/env)
    import importlib as _importlib

    import app.routes.root as _root_module

    _importlib.reload(_root_module)
    app.include_router(_root_module.router)
    return app


# Instantiate the app using the factory function
app = create_app()
