from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from domain.models.user_id import UserId

if TYPE_CHECKING:
    from domain.models.user import User


@dataclass
class Session:
    id: int | None
    user_id: UserId | None
    session_key: str
    created_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    user: User | None = None
