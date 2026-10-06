from flask import Blueprint, render_template

routes = Blueprint("routes", __name__)


@routes.get("/")
def index() -> str:
    return render_template("index.html")
