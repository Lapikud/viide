from flask import Flask

from viide.app.aka.manager import LinkManager
from viide.app.auth.clients.freeipa import FreeIpaClient
from viide.app.auth.manager import AuthManager
from viide.config import load_settings
from viide.db.engine import SqlDatabase
from viide.db.repositories.link import SqlLinkRepository
from viide.db.repositories.qr import SqlQrRepository
from viide.storage.client import S3Storage

from .extensions import csrf, login_manager
from .routes import routes


def create_app() -> Flask:
    settings = load_settings()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = settings.secret_key.get_secret_value()
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    csrf.init_app(app)
    login_manager.init_app(app)

    database = SqlDatabase(settings.database_url)
    storage = S3Storage(
        settings.storage_endpoint,
        settings.storage_public_url or settings.storage_endpoint,
        settings.storage_access_key,
        settings.storage_secret_key,
        settings.storage_bucket,
    )

    app.extensions["database"] = database
    app.extensions["storage"] = storage
    app.extensions["auth"] = AuthManager(FreeIpaClient(settings.freeipa_url))

    app.register_blueprint(routes)

    app.extensions["links"] = LinkManager(
        SqlLinkRepository(database),
        SqlQrRepository(database),
        storage,
        settings.public_url,
        reserved=frozenset(rule.rule.split("/")[1] for rule in app.url_map.iter_rules()),
    )

    return app
