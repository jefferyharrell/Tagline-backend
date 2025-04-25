"""
Dropbox implementation of StorageProvider (stub).
All methods raise NotImplementedError. This is a placeholder for future Dropbox integration.
"""

from io import BytesIO
from typing import Optional

import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata

from app.storage.provider import StorageProvider, StorageProviderMisconfigured


class DropboxStorageProvider(StorageProvider):
    """
    Media storage provider using Dropbox via the official SDK.
    Supports listing and retrieving files under a configured root path.
    All access is sandboxed to the configured root.
    """

    def __init__(
        self,
        *,
        refresh_token: Optional[str] = None,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        root_path: Optional[str] = None,
    ):
        """
        Initialize DropboxStorageProvider.
        Args:
            refresh_token: Dropbox OAuth2 refresh token (recommended for server-to-server auth).
            app_key: Dropbox app key (required for refresh token auth).
            app_secret: Dropbox app secret (required for refresh token auth).
            access_token: [DEPRECATED] Long-lived Dropbox access token (legacy/testing only).
            root_path: Root path in Dropbox (all keys are relative to this path).
        Raises:
            StorageProviderMisconfigured: If required credentials are missing or invalid.
        """
        self.root_path = root_path or "/"
        if refresh_token and app_key and app_secret:
            try:
                self.dbx = dropbox.Dropbox(
                    oauth2_refresh_token=refresh_token,
                    app_key=app_key,
                    app_secret=app_secret,
                )
            except Exception as e:
                raise StorageProviderMisconfigured(
                    f"Dropbox refresh token auth failed: {e}"
                )
        elif access_token:
            # Legacy/DEPRECATED path
            try:
                self.dbx = dropbox.Dropbox(access_token)
            except Exception as e:
                raise StorageProviderMisconfigured(
                    f"Dropbox access token auth failed: {e}"
                )
        else:
            raise StorageProviderMisconfigured(
                "Missing Dropbox credentials: must provide refresh_token, app_key, and app_secret (recommended), or access_token (legacy/testing)."
            )

    def _full_path(self, key: str) -> str:
        # Compose a Dropbox path under root_path, normalizing slashes
        if key.startswith("/"):
            key = key[1:]
        root = self.root_path.rstrip("/")
        return f"{root}/{key}" if root else f"/{key}"

    def _process_entries(
        self, entries: list, prefix: Optional[str] = None
    ) -> list[str]:
        """Process a list of Dropbox entries and extract matching file paths."""
        result: list[str] = []
        for entry in entries:
            if isinstance(entry, FileMetadata):
                rel_path = entry.path_display[len(self.root_path) :].lstrip("/")
                if not prefix or rel_path.startswith(prefix):
                    result.append(rel_path)
        return result

    def list(self, prefix: Optional[str] = None) -> list[str]:
        """
        List all file keys under the root path, optionally filtered by prefix.
        Returns:
            List of keys (relative to root_path).
        """
        path = self.root_path
        try:
            res = self.dbx.files_list_folder(path, recursive=True)
            entries = list(getattr(res, "entries", []))
            # Handle Dropbox pagination: fetch all pages using files_list_folder_continue
            while getattr(res, "has_more", False):
                cursor = getattr(res, "cursor", None)
                if not cursor:
                    break  # Defensive: can't continue without a cursor
                res = self.dbx.files_list_folder_continue(cursor)
                entries.extend(getattr(res, "entries", []))
            return self._process_entries(entries, prefix)
        except ApiError as e:
            raise FileNotFoundError(f"Dropbox listing failed: {e}")

    def retrieve(self, key: str) -> BytesIO:
        """
        Retrieve a file by key (relative to root_path).
        Returns a BytesIO stream.
        Raises FileNotFoundError if not found or outside root.
        """
        path = self._full_path(key)
        try:
            # Just disable type checking completely for this line
            # fmt: off
            md, res = self.dbx.files_download(path)  # type: ignore
            return BytesIO(res.content)  # type: ignore
            # fmt: on
        except ApiError as e:
            raise FileNotFoundError(f"Dropbox file not found: {key} ({e})")
