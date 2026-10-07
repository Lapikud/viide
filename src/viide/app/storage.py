"""The port for object storage, where QR images are kept."""

from datetime import timedelta
from typing import BinaryIO, Protocol

from pydantic import HttpUrl


class StorageUnavailable(Exception):
    """Report an unavailable object store."""

    message = "The storage service is unavailable."

    def __init__(self) -> None:
        """Set the error message."""
        super().__init__(self.message)


class Storage(Protocol):
    """Define how QR images are stored and retrieved."""

    def put(self, key: str, stream: BinaryIO, content_type: str) -> None:
        """Upload a stream under a storage key."""
        ...

    def get(self, key: str, expires_in: timedelta) -> HttpUrl:
        """Get a temporary URL for a stored object."""
        ...

    def delete(self, key: str) -> None:
        """Remove an object from storage."""
        ...
