"""
Health and diagnostics endpoints for Tagline backend.
"""

from fastapi import APIRouter, Depends, Request

from tagline_backend_app.deps import verify_api_key

router = APIRouter()


@router.get("/smoke-test")
def smoke_test(request: Request, _=Depends(verify_api_key)):
    """Health check: verifies storage provider config. Returns 200 if OK, 503 if misconfigured."""
    provider = request.app.state.get_photo_storage_provider(request.app)
    return {"status": "ok", "provider": type(provider).__name__}
