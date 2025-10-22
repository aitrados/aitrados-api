
from abc import ABC
from aitrados_api.trade_middleware.library.subscriber_mixin import AsyncSubscriberMixin
class AsyncSubscriber(AsyncSubscriberMixin,ABC):
    def __init__(self):
        super().__init__()
    async def on_news(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_ohlc(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_event(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_show_subscribe(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_authenticate(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_error(self, msg):
        """
         implement the method in your class
        """
        # raise NotImplementedError("method not implemented")


    async def on_handle_msg(self, msg):
        """
         implement the method in your class
        """
        # raise NotImplementedError("method not implemented")


    async def on_ohlc_chart_flow_streaming(self, msg):
        """
         implement the method in your class
        """
        #raise NotImplementedError("method not implemented")


    async def on_multi_symbol_multi_timeframe(self, msg):
        """
         implement the method in your class
        """
        # raise NotImplementedError("method not implemented")
