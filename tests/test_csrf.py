from flask.testing import FlaskClient

from .helpers import csrf_token


def test_app_rejects_form_without_csrf_token(client: FlaskClient):
    response = client.post(
        "/login", data={"username": "alice", "password": "secret"}
    )

    assert response.status_code == 400


def test_app_accepts_form_with_csrf_token(client: FlaskClient):
    token = csrf_token(client.get("/login"))
    data = {"username": "alice", "password": "secret", "csrf_token": token}

    response = client.post("/login", data=data)

    assert response.status_code == 302
