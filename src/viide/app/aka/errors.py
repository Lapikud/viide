"""URL shortening errors, with messages shown to users as written."""


class LinkError(Exception):
    """Base error for link operations."""

    message = "Something went wrong with the link."

    def __init__(self) -> None:
        """Set the error message shown to the user."""
        super().__init__(self.message)


class InvalidLink(LinkError):
    """Report invalid link input."""

    message = "Check the link details and try again."


class InvalidUrl(InvalidLink):
    """Report an invalid target URL."""

    message = "Enter a valid http(s) URL."


class InvalidShortCode(InvalidLink):
    """Report an invalid short code."""

    message = "Short codes can only contain letters, digits, - and _."


class InvalidExpiry(InvalidLink):
    """Report an invalid expiry period."""

    message = "Expiry must be between 1 and 3650 days."


class ShortCodeTaken(LinkError):
    """Report a short code collision."""

    message = "That short code is already taken."


class ShortCodeGenerationFailed(LinkError):
    """Report failed short code generation."""

    message = "Could not generate a short code. Please try again."


class ReservedShortCode(LinkError):
    """Report use of a reserved short code."""

    message = "That short code is reserved."


class LinkNotFound(LinkError):
    """Report a link that does not exist or is unavailable."""

    message = "Link not found."


class QrUnavailable(LinkError):
    """Report a QR code service failure."""

    message = "QR codes are unavailable right now."
