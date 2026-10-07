"""Authentication errors, with messages shown on the login form."""


class AuthError(Exception):
    """Base error for login failures."""

    message = "Authentication failed."

    def __init__(self) -> None:
        """Set the error message shown to the user."""
        super().__init__(self.message)


class MissingCredentials(AuthError):
    """Report missing login details."""

    message = "Enter your username and password."


class InvalidCredentials(AuthError):
    """Report rejected login details."""

    message = "Invalid username or password."


class AuthUnavailable(AuthError):
    """Report an unavailable authentication service."""

    message = "The authentication service is unavailable."
