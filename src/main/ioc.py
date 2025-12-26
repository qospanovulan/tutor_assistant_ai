from contextlib import contextmanager
from typing import Generator

from adapters.database.sqlalchemy import make_session_factory
# from adapters.database.sqlalchemy_uow import SqlAlchemyUoW
# from application.authenticate import Authenticate
# from application.common.id_provider import IdProvider
# from application.get_list_images import GetListImages
# from application.request_route_generation import RequestRouteGeneration
# from application.upload_image import UploadSourceImage
# from domain.services.artwork import ArtworkService
# from domain.services.source_image import SourceImageService
from presentation.interactor_factory import InteractorFactory


class IoC(InteractorFactory):

    def __init__(
            self,
            db_uri: str,
    ):
        self.db_uri = db_uri

        self.session_factory = make_session_factory(self.db_uri)


    # @contextmanager
    # def authenticate(self, id_provider: IdProvider) -> Generator[Authenticate, None, None]:
    #     session = self.session_factory()
    #     with SqlAlchemyUoW(session) as uow:
    #         user_gateway = UserGateway(uow.session)
    #         yield Authenticate(
    #             id_provider=id_provider,
    #             user_db_gateway=user_gateway,
    #             uow=uow,
    #         )
    #
    # @contextmanager
    # def get_uploaded_images(self, id_provider: IdProvider) -> Generator[GetListImages, None, None]:
    #     session = self.session_factory()
    #     with SqlAlchemyUoW(session) as uow:
    #         source_image_gateway = SourceImageGateway(uow.session)
    #         yield GetListImages(
    #             id_provider=id_provider,
    #             source_image_list_reader=source_image_gateway,
    #         )
    #
    # @contextmanager
    # def upload_source_image(self, id_provider: IdProvider) -> Generator[UploadSourceImage, None, None]:
    #     session = self.session_factory()
    #     with SqlAlchemyUoW(session) as uow:
    #         source_image_gateway = SourceImageGateway(uow.session)
    #         yield UploadSourceImage(
    #             id_provider=id_provider,
    #             source_image_saver=source_image_gateway,
    #             document_saver=self.local_storage,
    #             uow=uow,
    #             source_image_service=SourceImageService()
    #         )
    #
    # @contextmanager
    # def request_route_generation(self, id_provider: IdProvider) -> Generator[RequestRouteGeneration, None, None]:
    #     session = self.session_factory()
    #     with SqlAlchemyUoW(session) as uow:
    #         artworks_group_gateway = ArtworksGroupGateway(uow.session)
    #         source_image_gateway = SourceImageGateway(uow.session)
    #         yield RequestRouteGeneration(
    #             id_provider=id_provider,
    #             artworks_group_saver=artworks_group_gateway,
    #             route_generator=self.route_generator,
    #             uow=uow,
    #             artwork_service=ArtworkService(),
    #             source_image_reader=source_image_gateway,
    #         )
