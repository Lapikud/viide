"""The port that authentication clients implement to check credentials."""

from typing import Protocol

from .user import Credentials


class Client(Protocol):
    """Define how login credentials are checked."""

    def verify_credentials(self, creds: Credentials) -> bool:
        """Check if the credentials are valid."""
        ...
