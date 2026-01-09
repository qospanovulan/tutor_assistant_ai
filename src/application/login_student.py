from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import uuid4

from application.common.interactor import Interactor
from application.common.passwords import verify_password
from application.common.session_gateway import SessionReader, SessionSaver
from application.common.uow import UoW
from application.common.user_gateway import UserReader
from domain.exceptions.auth import AuthenticationError
from domain.models.session import Session
from domain.models.user_id import UserId


class UserDbGateway(UserReader, Protocol):
    pass


class SessionDbGateway(SessionReader, SessionSaver, Protocol):
    pass


@dataclass
class LoginStudentCommand:
    email: str
    password: str


@dataclass
class LoginStudentResult:
    user_id: UserId
    session_key: str
    full_name: str
    grade: int | None


class LoginStudent(Interactor[LoginStudentCommand, LoginStudentResult]):
    def __init__(
        self,
        user_db_gateway: UserDbGateway,
        session_db_gateway: SessionDbGateway,
        uow: UoW,
    ):
        self.user_db_gateway = user_db_gateway
        self.session_db_gateway = session_db_gateway
        self.uow = uow

    def __call__(self, data: LoginStudentCommand) -> LoginStudentResult:
        email = data.email.strip().lower()
        if "@" not in email or "." not in email:
            raise AuthenticationError("Email is invalid.")

        user = self.user_db_gateway.get_user_by_email(email)
        if not user:
            raise AuthenticationError("User not found.")
        if not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid credentials.")

        session_key = uuid4().hex
        session = Session(
            id=None,
            user_id=None,
            session_key=session_key,
            created_at=datetime.utcnow(),
            user=user,
        )
        self.session_db_gateway.save_session(session)
        self.uow.commit()

        grade = user.student_profile.grade if user.student_profile else None
        return LoginStudentResult(
            user_id=user.id,
            session_key=session_key,
            full_name=user.full_name or user.email,
            grade=grade,
        )
