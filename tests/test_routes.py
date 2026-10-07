from datetime import UTC, datetime, timedelta

import pytest
from flask.testing import FlaskClient

from viide.app.auth.errors import AuthUnavailable

from .fakes import FakeAuthClient, FakeLinkRepository, FakeStorage
from .helpers import login, post_with_csrf


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/"),
        ("GET", "/links"),
        ("POST", "/links"),
        ("POST", "/links/code/qr"),
        ("POST", "/links/code/delete"),
        ("POST", "/logout"),
    ],
)
def test_protected_pages_redirect_to_login(client: FlaskClient, method: str, path: str):
    response = post_with_csrf(client, path) if method == "POST" else client.get(path)

    assert response.headers["Location"].startswith("/login")


def test_login_redirects_to_index(client: FlaskClient):
    response = login(client)

    assert response.headers["Location"] == "/"


def test_wrong_password_shows_error(client: FlaskClient, auth_client: FakeAuthClient):
    auth_client.accepts = False

    response = login(client)

    assert "Invalid username or password." in response.text


def test_empty_form_shows_error(client: FlaskClient):
    response = post_with_csrf(client, "/login")

    assert "Enter your username and password." in response.text


def test_service_down_shows_error(client: FlaskClient, auth_client: FakeAuthClient):
    auth_client.error = AuthUnavailable()

    response = login(client)

    assert "The authentication service is unavailable." in response.text


def test_logged_in_user_skips_login_page(user_client: FlaskClient):
    response = user_client.get("/login")

    assert response.headers["Location"] == "/"


def test_logout_ends_session(user_client: FlaskClient):
    post_with_csrf(user_client, "/logout")

    response = user_client.get("/")

    assert response.status_code == 302


def test_creates_link(user_client: FlaskClient, links: FakeLinkRepository):
    post_with_csrf(
        user_client, "/links", {"src": "https://example.com", "dst": "code"}
    )

    assert links.rows["code"].created_by == "alice"


def test_new_link_is_shown(user_client: FlaskClient):
    data = {"src": "https://example.com", "dst": "code"}

    response = post_with_csrf(user_client, "/links", data, follow_redirects=True)

    assert "https://viide.test/code" in response.text


def test_invalid_link_shows_error(user_client: FlaskClient):
    response = post_with_csrf(
        user_client, "/links", {"src": "nope"}, follow_redirects=True
    )

    assert "Enter a valid http(s) URL." in response.text


def test_links_page_shows_only_own_links(user_client: FlaskClient, links: FakeLinkRepository):
    links.seed("mine")
    links.seed("theirs", created_by="bob")

    response = user_client.get("/links")

    assert "/mine" in response.text
    assert "/theirs" not in response.text


def test_links_page_shows_no_short_url_for_static_link(user_client: FlaskClient):
    post_with_csrf(user_client, "/links", {"src": "https://example.com/page", "static": "on"})

    response = user_client.get("/links")

    assert "https://example.com/page" in response.text
    assert "https://viide.test/" not in response.text


def test_deletes_link(user_client: FlaskClient, links: FakeLinkRepository):
    links.seed("code")

    post_with_csrf(user_client, "/links/code/delete")

    assert "code" not in links.rows


def test_deleting_other_users_link_shows_error(user_client: FlaskClient, links: FakeLinkRepository):
    links.seed("code", created_by="bob")

    response = post_with_csrf(
        user_client, "/links/code/delete", follow_redirects=True
    )

    assert "Link not found." in response.text


def test_creates_qr(user_client: FlaskClient, links: FakeLinkRepository, storage: FakeStorage):
    links.seed("code")

    post_with_csrf(user_client, "/links/code/qr")

    assert len(storage.objects) == 1


def test_qr_storage_failure_shows_error(
    user_client: FlaskClient, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")
    storage.fail_put = True

    response = post_with_csrf(user_client, "/links/code/qr", follow_redirects=True)

    assert "QR codes are unavailable right now." in response.text


def test_short_link_redirects(client: FlaskClient, links: FakeLinkRepository):
    links.seed("code")

    response = client.get("/code")

    assert response.headers["Location"] == "https://example.com/"


def test_missing_short_link_is_404(client: FlaskClient):
    response = client.get("/missing")

    assert response.status_code == 404


def test_expired_short_link_is_404(client: FlaskClient, links: FakeLinkRepository):
    links.seed("code", expires_at=datetime.now(UTC) - timedelta(days=1))

    response = client.get("/code")

    assert response.status_code == 404
