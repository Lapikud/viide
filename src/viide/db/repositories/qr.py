from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from viide.app.aka.qr import NewQrCode, QrCode, QrRepository
from viide.app.db import Database
from viide.db.models.qr import QrCode as QrRow


class SqlQrRepository(QrRepository):
    def __init__(self, db: Database[Session]) -> None:
        self.db = db

    def add(self, qr: NewQrCode) -> QrCode:
        with self.db.transaction() as transaction:
            row = transaction.scalar(insert(QrRow).values(**qr.model_dump()).returning(QrRow))
        return QrCode.model_validate(row)

    def get(self, qr_id: int) -> QrCode | None:
        with self.db.transaction() as transaction:
            row = transaction.get(QrRow, qr_id)
        return QrCode.model_validate(row) if row else None

    def delete(self, qr_id: int) -> None:
        with self.db.transaction() as transaction:
            transaction.execute(delete(QrRow).filter_by(id=qr_id))
