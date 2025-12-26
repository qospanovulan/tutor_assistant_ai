# from sqlalchemy.orm import Session
#
# from application.common.uow import UoW
#
#
# class SqlAlchemyUoW(UoW):
#     """
#     SQLAlchemy-backed Unit of Work.
#     Wraps a Session to provide commit/rollback/flush semantics.
#     """
#
#     def __init__(self, session: Session):
#         self.session: Session = session
#         self._is_active: bool = True
#
#     def flush(self) -> None:
#         if not self._is_active:
#             raise RuntimeError("UoW is already closed")
#         self.session.flush()
#
#     def rollback(self) -> None:
#         if not self._is_active:
#             return
#         self.session.rollback()
#         self._is_active = False
#
#     def commit(self) -> None:
#         if not self._is_active:
#             raise RuntimeError("UoW is already closed")
#         try:
#             self.session.commit()
#         except Exception:
#             self.session.rollback()
#             raise
#         finally:
#             self._is_active = False
#
#     def close(self) -> None:
#         if self._is_active:
#             try:
#                 self.session.close()
#             finally:
#                 self._is_active = False
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc, tb):
#         if exc_type is not None:
#             self.rollback()
#         self.close()
