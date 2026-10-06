from flask import Flask

from viide.app.auth.clients.ldap import LdapClient
from viide.app.auth.manager import AuthManager
from viide.config import load_settings
from viide.db.engine import create_db
from viide.storage.client import create_client

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
    app.extensions["auth"] = AuthManager(LdapClient(settings.ldap_url, settings.ldap_base_dn))

    app.register_blueprint(routes)

    return app
