"""
Health and diagnostics endpoints for Tagline backend.
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/smoke-test")
def smoke_test(request: Request):
    """Health check: verifies storage provider config. Returns 200 if OK, 503 if misconfigured."""
    provider = request.app.state.get_photo_storage_provider(request.app)
    return {"status": "ok", "provider": type(provider).__name__}
