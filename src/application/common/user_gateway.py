from abc import abstractmethod
from typing import Protocol

from domain.models.user import User
from domain.models.user_id import UserId


class UserReader(Protocol):
    @abstractmethod
    def get_user(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        raise NotImplementedError


class UserSaver(Protocol):
    @abstractmethod
    def save_user(self, user: User) -> None:
        raise NotImplementedError
