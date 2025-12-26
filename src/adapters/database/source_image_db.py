# from typing import List
#
# from sqlalchemy import select, func
# from sqlalchemy.orm import Session
#
# from application.common.source_image_gateway import SourceImageListReader, SourceImageSaver, SourceImageReader
# from domain.models.source_image import SourceImage, SourceImageId
# from domain.models.user_id import UserId
#
#
# class SourceImageGateway(
#     SourceImageListReader,
#     SourceImageSaver,
#     SourceImageReader,
# ):
#
#     def __init__(self, session: Session):
#         self.session = session
#
#     def find_source_images(
#             self,
#             user_id: UserId,
#             limit: int,
#             offset: int,
#     ) -> List[SourceImage]:
#         stmt = (
#             select(SourceImage)
#             .where(SourceImage.user_id == user_id)  # type: ignore[attr-defined]
#             .limit(limit)
#             .offset(offset)
#         )
#         return list(self.session.scalars(stmt))
#
#     def total_source_images(
#             self,
#             user_id: UserId,
#     ) -> int:
#         stmt = (
#             select(func.count())
#             .select_from(SourceImage)  # type: ignore[arg-type]
#             .where(SourceImage.user_id == user_id)  # type: ignore[attr-defined]
#         )
#         return self.session.scalar(stmt) or 0
#
#     def save_source_image(
#             self,
#             source_image: SourceImage,
#     ) -> SourceImage:
#         self.session.add(source_image)
#         self.session.flush()
#         return source_image
#
#     def get_source_image(
#             self,
#             id_: SourceImageId,
#     ) -> SourceImage:
#         stmt = (
#             select(SourceImage)
#             .where(SourceImage.id == id_)  # type: ignore[attr-defined]
#         )
#         return self.session.scalar(stmt)
