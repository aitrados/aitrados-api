import threading

from aitrados_api.trade_middleware.async_pubsub_intelligent_router import pubsub_intelligent_router_main
from aitrados_api.trade_middleware.async_rpc_intelligent_router import rpc_intelligent_router_main


class TradeMiddlewareRouterInstance:
    @classmethod
    def run_rpc_router(cls):
        router_thread = threading.Thread(target=rpc_intelligent_router_main,name="run_rpc_router")
        router_thread.daemon = True
        router_thread.start()

    @classmethod
    def run_pubsub_router(cls):
        router_thread = threading.Thread(target=pubsub_intelligent_router_main,name="run_pubsub_router")
        router_thread.daemon = True
        router_thread.start()