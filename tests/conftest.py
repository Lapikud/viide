from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pydantic import HttpUrl

from viide.app.aka.manager import LinkManager
from viide.config import Settings
from viide.web import app as web_app

from .fakes import FakeAuthClient, FakeLinkRepository, FakeQrRepository, FakeStorage
from .helpers import PUBLIC_URL, login

RESERVED = frozenset({"login", "logout", "links", "static"})


@pytest.fixture
def links() -> FakeLinkRepository:
    return FakeLinkRepository()


@pytest.fixture
def qr_codes() -> FakeQrRepository:
    return FakeQrRepository()


@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def auth_client() -> FakeAuthClient:
    return FakeAuthClient()


@pytest.fixture
def manager(
    links: FakeLinkRepository, qr_codes: FakeQrRepository, storage: FakeStorage
) -> LinkManager:
    return LinkManager(links, qr_codes, storage, HttpUrl(PUBLIC_URL), RESERVED)


def fake_settings() -> Settings:
    return Settings(
        _env_file=None,  # pyright: ignore[reportCallIssue]
        db_host="db.invalid",
        db_port=5432,
        db_name="viide",
        db_user="viide",
        db_password="unused",
        ldap_url="ldaps://ldap.invalid",
        ldap_base_dn="dc=test",
        freeipa_url="https://ipa.invalid",
        storage_endpoint="http://storage.invalid:3900",
        storage_public_url=None,
        storage_access_key="unused",
        storage_secret_key="unused",
        storage_bucket="viide",
        secret_key="test-secret",
        public_url=PUBLIC_URL,
    )


@pytest.fixture
def make_app(
    monkeypatch: pytest.MonkeyPatch,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
    auth_client: FakeAuthClient,
):

    def make() -> Flask:
        monkeypatch.setattr(web_app, "load_settings", fake_settings)
        app = web_app.create_app()
        app.config.update(TESTING=True)

        manager = app.extensions["links"]
        manager.links, manager.qr_codes, manager.storage = links, qr_codes, storage
        app.extensions["auth"].client = auth_client
        return app

    return make


@pytest.fixture
def app(make_app) -> Flask:
    return make_app()


@pytest.fixture
def client(app: Flask) -> Iterator[FlaskClient]:
    with app.test_client() as client:
        yield client


@pytest.fixture
def user_client(client: FlaskClient) -> FlaskClient:
    assert login(client).status_code == 302, "test client should log in successfully"
    return client
