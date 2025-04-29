"""
Rescan API route for Tagline backend.
"""

import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import verify_api_key

router = APIRouter()


# In-memory lock for scan idempotency (attach to app.state on startup)
def get_scan_lock(app):
    if not hasattr(app.state, "scan_lock"):
        app.state.scan_lock = asyncio.Lock()
    return app.state.scan_lock


@router.post("/scan", status_code=200)
def scan_photos(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(verify_api_key),
):
    """
    Async/idempotent scan endpoint. Starts a scan if not already running.
    Returns status: "started" or "already_running".
    """
    app = request.app
    scan_lock = get_scan_lock(app)
    if scan_lock.locked():
        return {"status": "already_running"}

    def scan_logic():
        # Placeholder for real scan logic
        provider = app.state.get_photo_storage_provider(app)
        repo = PhotoRepository(db)
        try:
            storage_files = set(f for f in provider.list() if isinstance(f, str))
            db_photos = repo.list()
            db_filenames = set(photo.filename for photo in db_photos)
            new_files = storage_files - db_filenames
            imported = []
            for fname in new_files:
                photo = repo.create(filename=fname)
                imported.append(photo.filename)
            # Optionally: store results in app.state for /health, etc.
        except Exception:
            # Log errors or store in app.state
            pass
        finally:
            # Release lock if needed (asyncio.Lock auto-releases with context mgr)
            pass

    async def scan_wrapper():
        async with scan_lock:
            scan_logic()

    background_tasks.add_task(scan_wrapper)
    return {"status": "started"}
