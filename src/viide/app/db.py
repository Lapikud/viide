"""The port for running database work in transactions."""

from contextlib import AbstractContextManager
from typing import Protocol


class Database[Trans](Protocol):
    """Define how to open a database transaction."""

    def transaction(self) -> AbstractContextManager[Trans]:
        """Open a transaction context for database operations."""
        ...
