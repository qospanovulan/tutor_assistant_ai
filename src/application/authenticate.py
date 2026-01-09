from typing import Protocol

from application.common.id_provider import IdProvider
from application.common.interactor import Interactor
from application.common.user_gateway import UserSaver, UserReader
from domain.exceptions.auth import AuthenticationError
from domain.models.user import User


class UserDbGateway(
    UserSaver, UserReader, Protocol,
):
    pass


class Authenticate(Interactor[None, User]):
    def __init__(
            self,
            id_provider: IdProvider,
            user_db_gateway: UserDbGateway,
    ):
        self.id_provider = id_provider
        self.user_db_gateway = user_db_gateway

    def __call__(self, data: None = None) -> User:
        user_id = self.id_provider.get_current_user_id()

        user = self.user_db_gateway.get_user(user_id)

        if user is None:
            raise AuthenticationError("User not found.")

        return user
