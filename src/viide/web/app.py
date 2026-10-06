from flask import Flask

from viide.app.auth.clients.ldap import LdapClient
from viide.app.auth.manager import AuthManager
from viide.config import load_settings
from viide.db.engine import SqlDatabase
from viide.storage.client import S3Storage

from .extensions import csrf, login_manager
from .routes import routes


def create_app() -> Flask:
    settings = load_settings()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.secret_key.get_secret_value()

    csrf.init_app(app)
    login_manager.init_app(app)

    app.extensions["database"] = SqlDatabase(settings.database_url)
    app.extensions["auth"] = AuthManager(LdapClient(settings.ldap_url, settings.ldap_base_dn))
    app.extensions["storage"] = S3Storage(
        settings.storage_endpoint,
        settings.storage_public_url or settings.storage_endpoint,
        settings.storage_access_key,
        settings.storage_secret_key,
        settings.storage_bucket,
    )

    app.register_blueprint(routes)

    return app
