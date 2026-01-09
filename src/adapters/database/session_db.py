from sqlalchemy.orm import Session as OrmSession

from application.common.session_gateway import SessionReader, SessionSaver
from domain.models.session import Session


class SessionGateway(SessionReader, SessionSaver):
    def __init__(self, session: OrmSession):
        self.session = session

    def get_session_by_key(self, session_key: str) -> Session | None:
        return (
            self.session.query(Session)
            .filter(Session.session_key == session_key)
            .one_or_none()
        )

    def save_session(self, session: Session) -> None:
        self.session.add(session)
