from abc import ABC, abstractmethod
from typing import ContextManager

from application.authenticate import Authenticate
from application.login_student import LoginStudent
from application.register_student import RegisterStudent
from application.common.id_provider import IdProvider


class InteractorFactory(ABC):

    @abstractmethod
    def authenticate(
            self, id_provider: IdProvider,
    ) -> ContextManager[Authenticate]:
        raise NotImplementedError

    @abstractmethod
    def register_student(self) -> ContextManager[RegisterStudent]:
        raise NotImplementedError

    @abstractmethod
    def login_student(self) -> ContextManager[LoginStudent]:
        raise NotImplementedError
