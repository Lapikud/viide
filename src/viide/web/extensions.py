"""Flask-Login and CSRF protection, shared across the web layer."""

from flask import current_app
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect

from viide.app.auth.user import SessionUser

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.blueprint_login_views["routes"] = "routes.login"


class LoginUser(UserMixin):
    """Adapt a session user for Flask-Login."""

    def __init__(self, user: SessionUser) -> None:
        """Wrap a session user for Flask-Login."""
        self.user = user
        self.id = user.id


@login_manager.user_loader
def load_user(user_id: str) -> LoginUser | None:
    """Load a Flask-Login user from the session ID."""
    user = current_app.extensions["auth"].load_user(user_id)
    return LoginUser(user) if user else None
