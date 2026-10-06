from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from viide.app.aka.errors import ShortCodeTaken
from viide.app.aka.links import Link, LinkRepository, NewLink
from viide.app.db import Database
from viide.db.models.link import Link as LinkRow


class SqlLinkRepository(LinkRepository):
    def __init__(self, db: Database[Session]) -> None:
        self.db = db

    def add(self, link: NewLink) -> Link:
        with self.db.transaction() as transaction:
            row = transaction.scalar(
                insert(LinkRow)
                .values(**link.model_dump())
                .on_conflict_do_nothing(index_elements=[LinkRow.dst])
                .returning(LinkRow)
            )
        if row is None:
            raise ShortCodeTaken
        return Link.model_validate(row)

    def get(self, dst: str) -> Link | None:
        with self.db.transaction() as transaction:
            row = transaction.scalar(select(LinkRow).filter_by(dst=dst))
        return Link.model_validate(row) if row else None

    def owned_by(self, created_by: str) -> list[Link]:
        with self.db.transaction() as transaction:
            rows = transaction.scalars(
                select(LinkRow).filter_by(created_by=created_by).order_by(LinkRow.created_at.desc())
            ).all()
        return [Link.model_validate(row) for row in rows]

    def connect(self, dst: str, qr_id: int) -> bool:
        with self.db.transaction() as transaction:
            connected = transaction.scalar(
                update(LinkRow)
                .where(LinkRow.dst == dst, LinkRow.connected_to.is_(None))
                .values(connected_to=qr_id)
                .returning(LinkRow.id)
            )
        return connected is not None

    def delete(self, dst: str) -> None:
        with self.db.transaction() as transaction:
            transaction.execute(delete(LinkRow).filter_by(dst=dst))
