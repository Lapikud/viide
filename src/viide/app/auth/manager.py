"""Authentication manager.

Authenticates users through a client and restores them from the session.
"""

from pydantic import SecretStr, ValidationError

from .client import Client
from .errors import InvalidCredentials, MissingCredentials
from .user import Credentials, SessionUser


class AuthManager:
    """Check credentials and create session users."""

    def __init__(self, client: Client) -> None:
        """Set the client used to check credentials."""
        self.client = client

    def login(self, username: str, password: SecretStr) -> SessionUser:
        """Validate credentials and return a session user."""
        try:
            creds = Credentials(username=username, password=password)
        except ValidationError as e:
            raise MissingCredentials from e

        if not self.client.verify_credentials(creds):
            raise InvalidCredentials
        return SessionUser(id=creds.username)

    def load_user(self, user_id: str) -> SessionUser | None:
        """Load a session user from a nonempty ID."""
        return SessionUser(id=user_id) if user_id else None
