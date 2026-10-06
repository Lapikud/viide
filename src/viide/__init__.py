import sys

from viide.web.app import create_app


def main() -> None:
    debug = "--debug" in sys.argv[1:]

    app = create_app()
    app.run(debug=debug)
