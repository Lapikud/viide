"""The pages and the public short link redirect."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from pydantic import SecretStr
from werkzeug.wrappers import Response

from viide.app.aka.errors import LinkError, LinkNotFound
from viide.app.auth.errors import AuthError

from .extensions import LoginUser

routes = Blueprint("routes", __name__)


@routes.get("/")
def index() -> str:
    """Render the QR and link creation page."""
    return render_template("index.html")


@routes.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Display the login form or sign in valid credentials."""
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))

    if request.method == "POST":
        try:
            user = current_app.extensions["auth"].login(
                request.form.get("username", ""),
                SecretStr(request.form.get("password", "")),
            )
        except AuthError as e:
            flash(str(e), "error")
        else:
            login_user(LoginUser(user))
            return redirect(url_for("routes.index"))

    return render_template("login.html")


@routes.post("/logout")
@login_required
def logout() -> Response:
    """End the current session and redirect to login."""
    logout_user()
    return redirect(url_for("routes.login"))


@routes.route("/links", methods=["GET", "POST"])
@login_required
def handle_links() -> Response | str:
    """List the user's links or create a new link."""
    links = current_app.extensions["links"]
    if request.method == "GET":
        return render_template("links.html", links=links.owned_by(current_user.id))

    try:
        link = links.shorten(
            request.form.get("src", ""),
            created_by=current_user.id,
            expires_in_days=request.form.get("expires_in_days"),
        )
    except LinkError as e:
        flash(str(e), "error")
    else:
        flash(str(links.short_url(link.dst)), "link")
    return redirect(url_for("routes.index"))


@routes.post("/static-qr")
def create_static_qr() -> str:
    """Generate a static QR directly from the submitted URL."""
    try:
        image = current_app.extensions["links"].create_qr(
            request.form.get("src", ""), static=True
        )
    except LinkError as e:
        flash(str(e), "error")
        return render_template("index.html")
    return render_template("index.html", static_qr=image)


@routes.post("/links/<dst>/qr")
@login_required
def create_qr(dst: str) -> Response | str:
    """Request a QR code for a link and show any error."""
    image = None
    try:
        image = current_app.extensions["links"].create_qr(dst, current_user.id)
    except LinkError as e:
        flash(str(e), "error")
    if image is not None:
        return render_template(
            "links.html",
            links=current_app.extensions["links"].owned_by(current_user.id),
            qr_image=image,
            qr_dst=dst,
        )
    return redirect(url_for("routes.handle_links"))


@routes.post("/links/<dst>/delete")
@login_required
def delete_link(dst: str) -> Response:
    """Delete a user's link and show any error."""
    try:
        current_app.extensions["links"].delete(dst, current_user.id)
    except LinkError as e:
        flash(str(e), "error")
    return redirect(url_for("routes.handle_links"))


@routes.get("/<dst>")
def follow(dst: str) -> Response:
    """Redirect a short code to its target or return 404."""
    try:
        link = current_app.extensions["links"].resolve(dst)
    except LinkNotFound:
        abort(404)
    return redirect(str(link.src))
