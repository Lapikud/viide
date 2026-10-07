"""Authentication client that binds to a FreeIPA LDAP directory."""

import logging
import ssl

from ldap3 import AUTO_BIND_NONE, Connection, Server, Tls
from ldap3.core.exceptions import (
    LDAPBindError,
    LDAPException,
    LDAPInvalidCredentialsResult,
    LDAPStartTLSError,
)
from ldap3.utils.dn import escape_rdn
from pydantic import BaseModel, ConfigDict

from viide.config import LdapUrl

from ..client import Client
from ..errors import AuthUnavailable
from ..user import Credentials

logger = logging.getLogger(__name__)


class Account(BaseModel):
    """Build a FreeIPA account name for LDAP."""

    model_config = ConfigDict(frozen=True)

    username: str
    base_dn: str

    def __str__(self) -> str:
        """Build the escaped LDAP name for the account."""
        return f"uid={escape_rdn(self.username)},cn=users,cn=accounts,{self.base_dn}"


class LdapClient(Client):
    """Check login credentials through LDAP."""

    def __init__(self, url: LdapUrl, base_dn: str) -> None:
        """Set the LDAP server and account base."""
        self.server = self.__create_server(url)
        self.base_dn = base_dn

    def verify_credentials(self, creds: Credentials) -> bool:
        """Check credentials by binding to LDAP."""
        try:
            with self.__create_connection(creds) as connection:
                connection.open()
                if not self.server.ssl and not connection.start_tls():
                    raise LDAPStartTLSError("Could not establish LDAP StartTLS")
                if not connection.bind():
                    raise LDAPBindError(connection.last_error or "LDAP bind failed")
        except LDAPInvalidCredentialsResult:
            return False
        except LDAPException as e:
            logger.exception("LDAP authentication failed")
            raise AuthUnavailable from e
        return True

    def __create_connection(self, creds: Credentials) -> Connection:
        """Build an LDAP connection for the account."""
        return Connection(
            self.server,
            user=str(self.__create_account(creds.username)),
            password=creds.password.get_secret_value(),
            auto_bind=AUTO_BIND_NONE,
            receive_timeout=5,
            raise_exceptions=True,
        )

    def __create_account(self, username: str) -> Account:
        """Build the LDAP account identifier for a username."""
        return Account(username=username, base_dn=self.base_dn)

    def __create_server(self, url: LdapUrl) -> Server:
        """Set up an LDAP server with TLS verification."""
        secure = url.scheme == "ldaps"
        port = url.port or (636 if secure else 389)

        return Server(
            # safe because the validator already checks that the host is available
            host=url.host or "",
            port=port,
            use_ssl=secure,
            tls=Tls(validate=ssl.CERT_REQUIRED),
            connect_timeout=5,
        )
