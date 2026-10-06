from pydantic import SecretStr, ValidationError

from .client import Client
from .errors import InvalidCredentials, MissingCredentials
from .user import Credentials, SessionUser


class AuthManager:
    def __init__(self, client: Client) -> None:
        self.client = client

    def login(self, username: str, password: SecretStr) -> SessionUser:
        try:
            creds = Credentials(username=username, password=password)
        except ValidationError as e:
            raise MissingCredentials from e

        if not self.client.verify_credentials(creds):
            raise InvalidCredentials
        return SessionUser(id=creds.username)

    def load_user(self, user_id: str) -> SessionUser | None:
        return SessionUser(id=user_id) if user_id else None
