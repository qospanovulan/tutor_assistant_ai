from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from typing import Protocol

from application.common.interactor import Interactor
from application.common.passwords import hash_password
from application.common.session_gateway import SessionReader, SessionSaver
from application.common.uow import UoW
from application.common.user_gateway import UserReader, UserSaver
from domain.exceptions.auth import RegistrationError
from domain.models.enums import UserRole
from domain.models.session import Session
from domain.models.user import StudentProfile, User
from domain.models.user_id import UserId


class UserDbGateway(UserReader, UserSaver, Protocol):
    pass


class SessionDbGateway(SessionReader, SessionSaver, Protocol):
    pass


@dataclass
class RegisterStudentCommand:
    full_name: str
    email: str
    password: str
    grade: int


@dataclass
class RegisterStudentResult:
    user_id: UserId
    session_key: str
    full_name: str
    grade: int


class RegisterStudent(Interactor[RegisterStudentCommand, RegisterStudentResult]):
    def __init__(
        self,
        user_db_gateway: UserDbGateway,
        session_db_gateway: SessionDbGateway,
        uow: UoW,
    ):
        self.user_db_gateway = user_db_gateway
        self.session_db_gateway = session_db_gateway
        self.uow = uow

    def __call__(self, data: RegisterStudentCommand) -> RegisterStudentResult:
        email = data.email.strip().lower()
        full_name = data.full_name.strip()

        if not full_name:
            raise RegistrationError("Name is required.")
        if "@" not in email or "." not in email:
            raise RegistrationError("Email is invalid.")
        if len(data.password) < 6:
            raise RegistrationError("Password must be at least 6 characters.")
        if not (1 <= data.grade <= 12):
            raise RegistrationError("Grade must be between 1 and 12.")

        existing = self.user_db_gateway.get_user_by_email(email)
        if existing:
            raise RegistrationError("User already exists.")

        user = User(
            id=None,
            email=email,
            password_hash=hash_password(data.password),
            role=UserRole.STUDENT,
            full_name=full_name,
        )
        user.student_profile = StudentProfile(user_id=None, grade=data.grade)

        self.user_db_gateway.save_user(user)
        self.uow.flush()
        if user.id is None:
            raise RegistrationError("Failed to create user.")

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

        return RegisterStudentResult(
            user_id=user.id,
            session_key=session_key,
            full_name=full_name,
            grade=data.grade,
        )
