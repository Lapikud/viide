from contextlib import AbstractContextManager
from typing import Protocol


class Database[Trans](Protocol):
    def transaction(self) -> AbstractContextManager[Trans]: ...
