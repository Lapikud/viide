from flask import current_app
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from viide.app.auth.user import SessionUser

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.blueprint_login_views["routes"] = "routes.login"


@login_manager.user_loader
def load_user(user_id: str) -> SessionUser | None:
    return current_app.extensions["auth"].load_user(user_id)
