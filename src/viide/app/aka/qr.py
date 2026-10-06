from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class NewQrCode(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    storage_key: str
    created_by: str


class QrCode(NewQrCode):
    id: int
    created_at: datetime


class QrRepository(Protocol):
    def add(self, qr: NewQrCode) -> QrCode: ...

    def get(self, qr_id: int) -> QrCode | None: ...

    def delete(self, qr_id: int) -> None: ...
