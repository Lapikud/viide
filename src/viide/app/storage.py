from datetime import timedelta
from typing import BinaryIO, Protocol

from pydantic import HttpUrl


class StorageUnavailable(Exception):
    message = "The storage service is unavailable."

    def __init__(self) -> None:
        super().__init__(self.message)


class Storage(Protocol):
    def put(self, key: str, stream: BinaryIO, content_type: str) -> None: ...

    def get(self, key: str, expires_in: timedelta) -> HttpUrl: ...

    def delete(self, key: str) -> None: ...
