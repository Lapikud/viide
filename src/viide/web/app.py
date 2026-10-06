from flask import Flask

from viide.config import load_settings
from viide.db.engine import create_db
from viide.storage.client import create_client
from viide.web.auth import create_auth_client

from .extensions import csrf, login_manager
from .routes import routes


def create_app() -> Flask:
    settings = load_settings()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.secret_key.get_secret_value()

    csrf.init_app(app)
    login_manager.init_app(app)

    app.extensions["database"] = create_db(settings)
    app.extensions["storage"] = create_client(settings)
    app.extensions["ldap"] = create_auth_client(settings)

    app.register_blueprint(routes)

    return app
