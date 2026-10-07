import pytest
from pydantic import SecretStr

from viide.app.auth.errors import AuthUnavailable, InvalidCredentials, MissingCredentials
from viide.app.auth.manager import AuthManager

from .fakes import FakeAuthClient


def test_login_returns_user(auth_client: FakeAuthClient):
    user = AuthManager(auth_client).login("alice", SecretStr("secret"))

    assert user.id == "alice", "login should return the authenticated user"


def test_login_strips_username(auth_client: FakeAuthClient):
    user = AuthManager(auth_client).login("  alice  ", SecretStr("secret"))

    assert user.id == "alice", "login should trim spaces around the username"


@pytest.mark.parametrize(("username", "password"), [("", "secret"), ("  ", "secret"), ("a", "")])
def test_login_without_credentials_fails(auth_client: FakeAuthClient, username, password):
    with pytest.raises(MissingCredentials):
        AuthManager(auth_client).login(username, SecretStr(password))
    assert auth_client.calls == 0, "the auth client should not run for blank credentials"


def test_login_rejects_credentials_when_client_rejects_them(auth_client: FakeAuthClient):
    auth_client.accepts = False

    with pytest.raises(InvalidCredentials):
        AuthManager(auth_client).login("alice", SecretStr("wrong"))
    assert auth_client.calls == 1, "the auth client should be called once"


def test_login_fails_when_service_is_down(auth_client: FakeAuthClient):
    auth_client.error = AuthUnavailable()

    with pytest.raises(AuthUnavailable):
        AuthManager(auth_client).login("alice", SecretStr("secret"))
