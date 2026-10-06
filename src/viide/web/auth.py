from ldap3 import Server

from viide.config import Settings


class LdapClient:
    def __init__(self, settings: Settings) -> None:
        self.server = Server(str(settings.ldap_url))
        self.base_dn = settings.ldap_base_dn


def create_auth_client(settings: Settings):
    return LdapClient(settings)
