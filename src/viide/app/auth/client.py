from abc import ABC, abstractmethod

from .user import Credentials


class Client(ABC):
    @abstractmethod
    def verify_credentials(self, creds: Credentials) -> bool: ...
