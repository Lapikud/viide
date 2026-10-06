class LinkError(Exception):
    message = "Something went wrong with the link."

    def __init__(self) -> None:
        super().__init__(self.message)


class InvalidLink(LinkError):
    message = "Enter an http(s) URL and a short code made of letters, digits, - or _."


class ShortCodeTaken(LinkError):
    message = "That short code is already taken."


class LinkNotFound(LinkError):
    message = "Link not found."
