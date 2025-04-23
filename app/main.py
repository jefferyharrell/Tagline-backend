from fastapi import FastAPI

from .config import get_settings
from .constants import APP_NAME
from .storage.filesystem import FilesystemPhotoStorageProvider


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=APP_NAME, version="0.1.0")
    # Storage provider selection logic
    if settings.STORAGE_PROVIDER.lower() in ("filesystem", "", None):
        # If you want to use the provider later, attach it to app.state
        app.state.photo_storage_provider = FilesystemPhotoStorageProvider(
            settings.filesystem_photo_storage.path
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
    # TODO: When adding more providers, extend the selection logic above.
    # ...add routes, dependencies, etc. here...
    # Register routes dynamically (reload to pick up changes/env)
    import importlib as _importlib

    import app.routes.root as _root_module

    _importlib.reload(_root_module)
    # Register the APIRouter instance from the module
    app.include_router(_root_module.router)
    return app
