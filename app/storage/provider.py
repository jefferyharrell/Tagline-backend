"""
Abstract base class for item storage providers.
This interface is agnostic to backend details (filesystem, cloud, etc).
Providers should be configured via their constructor and/or environment/config.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Iterable, Optional


class StorageProviderMisconfigured(Exception):
    """
    Raised when a storage provider is misconfigured (e.g., missing required env vars).
    """

    pass


class StorageProvider(ABC):
    """
    Abstract interface for item storage providers.
    All implementations must be stateless except for configuration passed at init.
    """

    @abstractmethod
    def list(self, prefix: Optional[str] = None) -> Iterable[str]:
        """
        List all item keys (filenames/IDs) in storage, optionally filtered by prefix.
        Returns an iterable of string keys.
        """
        pass

    @abstractmethod
    def retrieve(self, key: str) -> BinaryIO:
        """
        Retrieve a item by key. Returns a file-like object (opened in binary mode).
        Raises FileNotFoundError if not found.
        """
        pass

    def upload(self, key: str, data: BinaryIO) -> None:
        """
        Uploading items is not supported in Tagline (read-only app).
        This method is reserved for future use.
        """
        raise NotImplementedError(
            "Photo upload is not supported in Tagline. This method is reserved for future use."
        )

    def delete(self, key: str) -> None:
        """
        Deleting items is not supported in Tagline (read-only app).
        This method is reserved for future use.
        """
        raise NotImplementedError(
            "Photo deletion is not supported in Tagline. This method is reserved for future use."
        )

    # Optionally, add a method for generating public URLs (for S3, etc)
    def get_url(self, key: str) -> Optional[str]:
        """
        Return a public URL for the item, if supported by the backend.
        Default: None (not supported).
        """
        return None
