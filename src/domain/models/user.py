from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from domain.models.enums import UserRole

from .user_id import UserId

if TYPE_CHECKING:
    from domain.models.session import Session


@dataclass
class User:
    id: UserId | None
    email: str
    password_hash: str
    role: UserRole
    full_name: str | None = None
    created_at: datetime | None = None
    student_profile: StudentProfile | None = None
    sessions: list[Session] = field(default_factory=list)


@dataclass
class StudentProfile:
    user_id: UserId | None
    grade: int
    user: User | None = None
