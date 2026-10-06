from pydantic import AnyUrl, HttpUrl, PostgresDsn, SecretStr, UrlConstraints, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LdapUrl(AnyUrl):
    _constraints = UrlConstraints(allowed_schemes=["ldap", "ldaps"], host_required=True)


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "viide"
    db_password: SecretStr

    ldap_url: LdapUrl = LdapUrl("ldaps://ipa.lapikud.ee")
    ldap_base_dn: str = "dc=lapikud,dc=ee"
    freeipa_url: HttpUrl = HttpUrl("https://ipa.lapikud.ee")

    storage_endpoint: AnyUrl = AnyUrl.build(scheme="http", port=3900, host="localhost")
    storage_public_url: AnyUrl | None = None
    storage_access_key: SecretStr
    storage_secret_key: SecretStr
    storage_bucket: str = "viide"

    secret_key: SecretStr
    public_url: HttpUrl = HttpUrl("http://localhost:5000")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @computed_field
    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            path=self.db_name,
        )


def load_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
