import re

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

PUBLIC_URL = "https://viide.test"


def login(client: FlaskClient, username: str = "alice", password: str = "secret") -> TestResponse:
    return post_with_csrf(client, "/login", {"username": username, "password": password})


def csrf_token(response: TestResponse) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match, "page has no CSRF token"
    return match.group(1)


def post_with_csrf(
    client: FlaskClient, path: str, data: dict[str, str] | None = None, **kwargs
) -> TestResponse:
    form_data = dict(data or {})
    form_data["csrf_token"] = csrf_token(client.get("/login", follow_redirects=True))
    return client.post(path, data=form_data, **kwargs)
