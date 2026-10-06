import logging

import httpx
from pydantic import HttpUrl

from ..client import Client
from ..errors import AuthUnavailable
from ..user import Credentials

logger = logging.getLogger(__name__)


class FreeIpaClient(Client):
    def __init__(self, url: HttpUrl) -> None:
        origin = str(url).rstrip("/")
        self.http = httpx.Client(
            base_url=origin,
            headers={"Referer": f"{origin}/ipa", "Accept": "text/plain"},
            timeout=10,
        )

    def verify_credentials(self, creds: Credentials) -> bool:
        try:
            response = self.http.post(
                "/ipa/session/login_password",
                data={"user": creds.username, "password": creds.password.get_secret_value()},
            )
        except httpx.HTTPError as e:
            logger.exception("FreeIPA authentication failed")
            raise AuthUnavailable from e

        if response.status_code == httpx.codes.UNAUTHORIZED:
            return False
        if response.is_success:
            return True

        logger.error("FreeIPA login returned HTTP %s", response.status_code)
        raise AuthUnavailable
