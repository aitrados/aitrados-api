import threading
import time

from aitrados_api.common_lib.common import run_asynchronous_function
from aitrados_api.trade_middleware.router_instance import TradeMiddlewareRouterInstance
from aitrados_api.trade_middleware_service.trade_middleware_rpc_service import AitradosApiBackendService


class AitradosTradeMiddlewareInstance(TradeMiddlewareRouterInstance):

    @classmethod
    def run_all(cls):
        cls.run_rpc_router()
        cls.run_pubsub_router()
        time.sleep(0.2)
        cls.run_aitrados_api_service()
    @classmethod
    def run_aitrados_api_service(cls):
        #api_service
        def _api_service():
            from aitrados_api.trade_middleware.response import AsyncBackendResponse
            bs = AitradosApiBackendService()
            service = AsyncBackendResponse(bs)
            run_asynchronous_function(service.init())
        router_thread = threading.Thread(target=_api_service,name="run_aitrados_api_service")
        router_thread.daemon = True
        router_thread.start()