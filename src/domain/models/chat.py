from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from domain.models.enums import ChatKind, MessageRole

if TYPE_CHECKING:
    from domain.models.user import User


@dataclass
class ChatSession:
    id: int | None
    user_id: int
    kind: ChatKind = ChatKind.ASSISTANT_CHAT
    created_at: datetime | None = None
    user: User | None = None
    messages: list[ChatMessage] = field(default_factory=list)


@dataclass
class ChatMessage:
    id: int | None
    session_id: int
    role: MessageRole
    content: str
    created_at: datetime | None = None
    session: ChatSession | None = None
