"""Login credentials and the authenticated user.

Users are known only by their username, which is also the owner recorded on links.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints


class Credentials(BaseModel):
    """Validate a username and password."""

    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    password: SecretStr = Field(min_length=1)


class SessionUser(BaseModel):
    """Identify the user in a session."""

    model_config = ConfigDict(frozen=True)

    id: str
