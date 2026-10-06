class LinkError(Exception):
    message = "Something went wrong with the link."

    def __init__(self) -> None:
        super().__init__(self.message)


class InvalidLink(LinkError):
    message = "Check the link details and try again."


class InvalidUrl(InvalidLink):
    message = "Enter a valid http(s) URL."


class InvalidShortCode(InvalidLink):
    message = "Short codes can only contain letters, digits, - and _."


class InvalidExpiry(InvalidLink):
    message = "Expiry must be between 1 and 3650 days."


class ShortCodeTaken(LinkError):
    message = "That short code is already taken."


class ReservedShortCode(LinkError):
    message = "That short code is reserved."


class LinkNotFound(LinkError):
    message = "Link not found."


class QrUnavailable(LinkError):
    message = "QR codes are unavailable right now."
