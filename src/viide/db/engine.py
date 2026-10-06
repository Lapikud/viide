from collections.abc import Generator
from contextlib import contextmanager

from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from viide.app.db import Database


class SqlDatabase(Database[Session]):
    def __init__(self, url: PostgresDsn) -> None:
        self.engine = create_engine(str(url))
        self.transactions = sessionmaker(bind=self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self) -> Generator[Session]:
        with self.transactions.begin() as transaction:
            yield transaction
