from typing import Annotated

from flask_login import UserMixin
from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints


class Credentials(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    password: SecretStr = Field(min_length=1)


class SessionUser(BaseModel, UserMixin):
    model_config = ConfigDict(frozen=True)

    id: str
