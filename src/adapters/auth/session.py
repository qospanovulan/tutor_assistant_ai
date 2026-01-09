from __future__ import annotations

from datetime import datetime

from application.common.id_provider import IdProvider
from application.common.session_gateway import SessionReader
from domain.exceptions.auth import AuthenticationError
from domain.models.user_id import UserId


class SessionIdProvider(IdProvider):
    def __init__(
        self,
        session_gateway: SessionReader,
        session_key: str | None,
    ):
        self.session_gateway = session_gateway
        self.session_key = session_key

    def get_current_user_id(self) -> UserId:
        if not self.session_key:
            raise AuthenticationError("Missing session key.")

        session = self.session_gateway.get_session_by_key(self.session_key)
        if not session:
            raise AuthenticationError("Session not found.")
        if session.revoked_at is not None:
            raise AuthenticationError("Session revoked.")
        if session.expires_at is not None and session.expires_at <= datetime.utcnow():
            raise AuthenticationError("Session expired.")

        if session.user_id is None:
            raise AuthenticationError("Session is not bound to a user.")

        return UserId(int(session.user_id))
