class AuthError(Exception):
    message = "Authentication failed."

    def __init__(self) -> None:
        super().__init__(self.message)


class MissingCredentials(AuthError):
    message = "Enter your username and password."


class InvalidCredentials(AuthError):
    message = "Invalid username or password."


class AuthUnavailable(AuthError):
    message = "The authentication service is unavailable."
