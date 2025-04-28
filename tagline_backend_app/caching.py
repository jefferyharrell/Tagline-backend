"""Caching utilities, primarily for thumbnails."""

import logging
from typing import Optional

from cachetools import LRUCache

from tagline_backend_app.config import get_settings

# Global thumbnail cache instance (initialized later)
THUMBNAIL_CACHE: Optional[LRUCache] = None


def initialize_thumbnail_cache():
    """Initializes the global thumbnail cache based on environment settings."""
    global THUMBNAIL_CACHE
    settings = get_settings()

    max_size_mb = settings.THUMBNAIL_CACHE_MAX_MB
    # Estimate cache item size (512x512 WebP can vary, using a rough estimate)
    # Assume avg 50KB per thumbnail for sizing calculation
    avg_thumbnail_size_kb = 50
    max_items = int((max_size_mb * 1024) / avg_thumbnail_size_kb)

    if max_items <= 0:
        logging.warning(
            f"Calculated max_items for thumbnail cache is {max_items}. "
            f"Disabling cache. Check THUMBNAIL_CACHE_MAX_MB ({max_size_mb}MB)."
        )
        THUMBNAIL_CACHE = None  # Explicitly disable if size is too small
        return

    logging.info(
        f"Initializing thumbnail LRU cache: max_size={max_size_mb}MB, "
        f"estimated max_items={max_items} (assuming ~{avg_thumbnail_size_kb}KB/thumb)"
    )
    # Note: cachetools maxsize is number of items, not bytes
    THUMBNAIL_CACHE = LRUCache(maxsize=max_items)


def get_thumbnail_cache() -> Optional[LRUCache]:
    """Returns the initialized global thumbnail cache instance."""
    if THUMBNAIL_CACHE is None:
        logging.warning(
            "Thumbnail cache accessed before initialization or is disabled."
        )
    return THUMBNAIL_CACHE
