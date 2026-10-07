"""Viide, a URL shortener and QR code service.

Serves the app with Flask.
"""

import sys

from viide.web.app import create_app


def main() -> None:
    """Start the web server, enabling debug mode when requested."""
    debug = "--debug" in sys.argv[1:]

    app = create_app()
    app.run(debug=debug)
