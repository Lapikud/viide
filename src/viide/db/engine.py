"""The PostgreSQL connection shared by every repository."""

from collections.abc import Generator
from contextlib import contextmanager

from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from viide.app.db import Database


class SqlDatabase(Database[Session]):
    """Open SQLAlchemy sessions inside transactions."""

    def __init__(self, url: PostgresDsn) -> None:
        """Create the SQL engine and transaction factory."""
        self.engine = create_engine(str(url), pool_pre_ping=True)
        self.transactions = sessionmaker(bind=self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self) -> Generator[Session]:
        """Create a transaction session that commits or rolls back on exit."""
        with self.transactions.begin() as transaction:
            yield transaction
