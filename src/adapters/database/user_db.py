from sqlalchemy.orm import Session, joinedload

from application.common.user_gateway import UserReader, UserSaver
from domain.models.user import User
from domain.models.user_id import UserId


class UserGateway(UserReader, UserSaver):

    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: UserId) -> User | None:
        return (
            self.session.query(User)
            .options(joinedload(User.student_profile))
            .filter(User.id == user_id)
            .one_or_none()
        )

    def get_user_by_email(self, email: str) -> User | None:
        return (
            self.session.query(User)
            .options(joinedload(User.student_profile))
            .filter(User.email == email)
            .one_or_none()
        )

    def save_user(self, user: User) -> None:
        self.session.add(user)
