from abc import ABC, abstractmethod
from typing import ContextManager

# from application.authenticate import Authenticate
# from application.common.id_provider import IdProvider
# from application.get_list_images import GetListImages
# from application.request_route_generation import RequestRouteGeneration
# from application.upload_image import UploadSourceImage


class InteractorFactory(ABC):
    pass
    # @abstractmethod
    # def authenticate(
    #         self, id_provider: IdProvider,
    # ) -> ContextManager[Authenticate]:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def get_uploaded_images(
    #         self, id_provider: IdProvider,
    # ) -> ContextManager[GetListImages]:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def upload_source_image(
    #         self, id_provider: IdProvider,
    # ) -> ContextManager[UploadSourceImage]:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # def request_route_generation(
    #         self, id_provider: IdProvider
    # ) -> ContextManager[RequestRouteGeneration]:
    #     raise NotImplementedError
