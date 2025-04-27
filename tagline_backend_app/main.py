from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from tagline_backend_app.config import get_settings
from tagline_backend_app.constants import APP_NAME
from tagline_backend_app.redis_token_store import RedisTokenStore
from tagline_backend_app.storage.filesystem import (
    StorageProviderMisconfigured,
)
from tagline_backend_app.storage.memory import InMemoryStorageProvider
from tagline_backend_app.storage.null import NullStorageProvider


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

    # Enable CORS if allowed origins are set
    allowed_origins = [
        o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()
    ]
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register global exception handler for StorageProviderMisconfigured
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

    # Add this new handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Custom handler for HTTPException to prevent logging tracebacks
        for expected client errors (4xx).
        """
        # Optionally, log a simple info message without traceback
        # logger.info(f"HTTPException handled: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),  # Include headers if present
        )

    # Store provider config (not the instance) for lazy instantiation
    provider_kind = (
        settings.STORAGE_PROVIDER.lower() if settings.STORAGE_PROVIDER else "filesystem"
    )
    if provider_kind in ("filesystem", "", None):
        app.state.photo_storage_provider_kind = "filesystem"
        app.state.filesystem_storage_path = settings.filesystem_storage.path
    elif provider_kind == "null":
        app.state.photo_storage_provider_kind = "null"
    elif provider_kind == "memory":
        app.state.photo_storage_provider_kind = "memory"
    elif provider_kind == "dropbox":
        app.state.photo_storage_provider_kind = "dropbox"
        # Build a config dict for the provider
        dropbox_cfg = {
            "refresh_token": settings.dropbox_refresh_token,
            "app_key": settings.dropbox_app_key,
            "app_secret": settings.dropbox_app_secret,
            "access_token": settings.dropbox_access_token,
            "root_path": settings.dropbox_root_path,
        }
        # Fail fast if required fields are missing
        if not (
            dropbox_cfg["refresh_token"]
            and dropbox_cfg["app_key"]
            and dropbox_cfg["app_secret"]
        ):
            raise RuntimeError(
                "DROPBOX provider selected but config is missing (check env vars)"
            )
        app.state.dropbox_provider_config = dropbox_cfg

    else:
        raise NotImplementedError(
            f"Storage provider '{settings.STORAGE_PROVIDER}' is not supported yet. "
            "Available: filesystem, null, memory."
        )

    # Helper for lazy provider instantiation
    def get_photo_storage_provider(app_instance):
        kind = getattr(app_instance.state, "photo_storage_provider_kind", None)
        if kind == "filesystem":
            from tagline_backend_app.storage.filesystem import FilesystemStorageProvider

            return FilesystemStorageProvider(app_instance.state.filesystem_storage_path)
        elif kind == "null":
            return NullStorageProvider()
        elif kind == "memory":
            return InMemoryStorageProvider()
        elif kind == "dropbox":
            from tagline_backend_app.storage.dropbox import DropboxStorageProvider

            cfg = getattr(app_instance.state, "dropbox_provider_config", None)
            if not cfg:
                raise StorageProviderMisconfigured(
                    "Dropbox config missing from app state"
                )
            return DropboxStorageProvider(
                refresh_token=cfg["refresh_token"],
                app_key=cfg["app_key"],
                app_secret=cfg["app_secret"],
                access_token=cfg["access_token"],
                root_path=cfg["root_path"],
            )
        raise NotImplementedError(
            "Only filesystem, null, memory, and dropbox providers are supported."
        )

    app.state.get_photo_storage_provider = get_photo_storage_provider
    # Wire up RedisTokenStore
    app.state.token_store = RedisTokenStore(
        settings.REDIS_URL or "redis://localhost:6379/0"
    )
    # Register routes dynamically (reload to pick up changes/env)
    import importlib as _importlib

    import tagline_backend_app.routes.root as _root_module

    _importlib.reload(_root_module)
    app.include_router(_root_module.router)
    return app


# Instantiate the app using the factory function
app = create_app()
