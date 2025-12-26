# from sqlalchemy.orm import Session
#
# from application.common.user_gateway import UserReader, UserSaver
# from domain.models.user import User
# from domain.models.user_id import UserId
#
#
# class UserGateway(UserReader, UserSaver):
#
#     def __init__(self, session: Session):
#         self.session = session
#
#     def get_user(self, user_id: UserId) -> User | None:
#         return self.session.get(User, user_id)
#
#     def save_user(self, user: User) -> None:
#         self.session.add(user)
