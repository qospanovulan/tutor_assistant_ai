from abc import abstractmethod
from typing import Protocol

from domain.models.session import Session


class SessionReader(Protocol):
    @abstractmethod
    def get_session_by_key(self, session_key: str) -> Session | None:
        raise NotImplementedError


class SessionSaver(Protocol):
    @abstractmethod
    def save_session(self, session: Session) -> None:
        raise NotImplementedError
