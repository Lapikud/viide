"""QR code models and their repository port.

Each record points to an image kept in object storage.
"""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class NewQrCode(BaseModel):
    """Hold QR code data before it is saved."""

    model_config = ConfigDict(frozen=True, from_attributes=True)

    storage_key: str
    created_by: str


class QrCode(NewQrCode):
    """Hold a saved QR code record."""

    id: int
    created_at: datetime


class QrRepository(Protocol):
    """Define how QR code records are stored."""

    def add(self, qr: NewQrCode) -> QrCode:
        """Store and return a QR code record."""
        ...

    def get(self, qr_id: int) -> QrCode | None:
        """Find a QR code by ID."""
        ...

    def delete(self, qr_id: int) -> None:
        """Remove a QR code by ID."""
        ...
