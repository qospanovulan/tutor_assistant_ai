from contextlib import contextmanager
from typing import Generator

from adapters.database.sqlalchemy import make_session_factory
from adapters.database.sqlalchemy_uow import SqlAlchemyUoW
from adapters.database.session_db import SessionGateway
from adapters.database.user_db import UserGateway
from application.authenticate import Authenticate
from application.common.id_provider import IdProvider
from application.login_student import LoginStudent
from application.register_student import RegisterStudent
from presentation.interactor_factory import InteractorFactory


class IoC(InteractorFactory):

    def __init__(
            self,
            db_uri: str,
    ):
        self.db_uri = db_uri

        self.session_factory = make_session_factory(self.db_uri)


    @contextmanager
    def authenticate(self, id_provider: IdProvider) -> Generator[Authenticate, None, None]:
        session = self.session_factory()
        try:
            user_gateway = UserGateway(session)
            yield Authenticate(
                id_provider=id_provider,
                user_db_gateway=user_gateway,
            )
        finally:
            session.close()

    @contextmanager
    def register_student(self) -> Generator[RegisterStudent, None, None]:
        session = self.session_factory()
        with SqlAlchemyUoW(session) as uow:
            user_gateway = UserGateway(uow.session)
            session_gateway = SessionGateway(uow.session)
            yield RegisterStudent(
                user_db_gateway=user_gateway,
                session_db_gateway=session_gateway,
                uow=uow,
            )

    @contextmanager
    def login_student(self) -> Generator[LoginStudent, None, None]:
        session = self.session_factory()
        with SqlAlchemyUoW(session) as uow:
            user_gateway = UserGateway(uow.session)
            session_gateway = SessionGateway(uow.session)
            yield LoginStudent(
                user_db_gateway=user_gateway,
                session_db_gateway=session_gateway,
                uow=uow,
            )
