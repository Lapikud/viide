from typing import Protocol

from .user import Credentials


class Client(Protocol):
    def verify_credentials(self, creds: Credentials) -> bool: ...
