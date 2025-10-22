from aitrados_api.trade_middleware.backend_service import BackendService
from aitrados_api.trade_middleware.library.response_mixin import AsyncBackendResponseMixin


class AsyncBackendResponse(AsyncBackendResponseMixin):
    def __init__(self, backend_service:BackendService,backend_identity:str=None):
        """
        :param backend_service:
        :param backend_identity: if this is None, then, backend_service.IDENTITY.backend_identity exists
        """
        super().__init__(backend_service,backend_identity)