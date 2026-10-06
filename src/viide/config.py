from pydantic import AnyUrl, PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str = "viide"
    db_password: SecretStr

    ldap_url: str = "ldaps://ipa.lapikud.ee"
    ldap_base_dn: str = "dc=lapikud,dc=ee"

    storage_endpoint: AnyUrl = AnyUrl.build(scheme="http", port=3900, host="localhost")
    storage_access_key: SecretStr
    storage_secret_key: SecretStr
    storage_bucket: str = "viide"

    secret_key: SecretStr

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
