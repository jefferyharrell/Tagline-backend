from fastapi import FastAPI

from .config import get_settings
from .constants import APP_NAME
from .redis_token_store import RedisTokenStore
from .storage.filesystem import (
    StorageProviderMisconfigured,
)


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

    # Register global exception handler for StorageProviderMisconfigured
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @app.exception_handler(StorageProviderMisconfigured)
    async def storage_provider_misconfigured_handler(
        request: Request, exc: StorageProviderMisconfigured
    ):
        return JSONResponse(
            status_code=503,
            content={
                "error": "StorageProviderMisconfigured",
                "detail": str(exc),
            },
        )

    # Store provider config (not the instance) for lazy instantiation
    if settings.STORAGE_PROVIDER.lower() in ("filesystem", "", None):
        app.state.photo_storage_provider_kind = "filesystem"
        app.state.filesystem_storage_path = settings.filesystem_storage.path
    elif settings.STORAGE_PROVIDER.lower() == "dropbox":
        raise NotImplementedError(
            "DropboxPhotoStorageProvider is not implemented yet. "
            "Set STORAGE_PROVIDER=filesystem or implement Dropbox support."
        )
    else:
        raise NotImplementedError(
            f"Storage provider '{settings.STORAGE_PROVIDER}' is not supported yet."
        )

    # Helper for lazy provider instantiation
    def get_photo_storage_provider(app_instance):
        if (
            getattr(app_instance.state, "photo_storage_provider_kind", None)
            == "filesystem"
        ):
            from .storage.filesystem import FilesystemPhotoStorageProvider

            return FilesystemPhotoStorageProvider(
                app_instance.state.filesystem_storage_path
            )
        raise NotImplementedError("Only filesystem provider is supported.")

    app.state.get_photo_storage_provider = get_photo_storage_provider
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
