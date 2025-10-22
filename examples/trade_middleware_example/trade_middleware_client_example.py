import time
from loguru import logger

from aitrados_api.common_lib.any_list_data_to_format_data import ApiListResultToFormatData2, AnyListDataToFormatData, \
    deserialize_multi_symbol_multi_timeframe_data
from aitrados_api.common_lib.contant import SchemaAsset, IntervalName
from aitrados_api.trade_middleware.request import FrontendRequest, AsyncFrontendRequest
from aitrados_api.trade_middleware.subscriber import AsyncSubscriber

from aitrados_api.trade_middleware_service.trade_middleware_identity import aitrados_api_identity as idt
"""
at first ,run "python run_trade_middleware_example.py"
"""

class MyAsyncSubscriber(AsyncSubscriber):
    """
    Asynchronous function callback
    """

    async def on_my_first_sub_topic(self, msg):
        #my_first_sub_topic is from custom_pub_service_example.py
        print("on_my_first_sub_topic", msg)
        pass
    async def on_news(self, msg):
        print("on_news", msg)
        pass
    async def on_ohlc(self, msg):
        #print("on_ohlc",AnyListDataToFormatData(msg).get_polars())
        pass
    async def on_event(self, msg):
        print("on_event", AnyListDataToFormatData(msg).get_csv())
        pass
    async def on_show_subscribe(self, msg):
        print("on_show_subscribe",msg)
        all_subscribed_topics = await AsyncFrontendRequest.call_sync(idt.backend_identity,fun.ALL_SUBSCRIBED_TOPICS)
        print("all_subscribed_topics",all_subscribed_topics)
        pass
    async def on_authenticate(self, msg):
        print("on_authenticate",msg)
        pass
    async def on_error(self, msg):
        print( "on_error",msg)
        pass

    async def on_ohlc_chart_flow_streaming(self, msg):
        try:

            full_symbol = msg["full_symbol"]
            interval = msg["interval"]
            df = AnyListDataToFormatData(msg["data"]).get_polars()
            print("on_ohlc_chart_flow_streaming",full_symbol,interval)
        except:
            logger.error(f"11error:{msg},smg类型,{type(msg)}")
    async def on_multi_symbol_multi_timeframe(self, msg):
        name=msg["name"]
        data=deserialize_multi_symbol_multi_timeframe_data(msg["data"], to_format="pandas")
        #print( "on_multi_symbol_multi_timeframe",name)



    async def on_handle_msg(self, msg):
        #here will receive all msgs
        pass





channel=idt.channel
fun=idt.fun

class MyRequestTest:
    @staticmethod
    def request_sub_multi_symbol_multi_timeframe_example():
        #refer to latest_ohlc_multi_timeframe_alignment.py
        data_list=[
            {
                "item_data" : {
            "CRYPTO:GLOBAL:BTCUSD": [IntervalName.M15, IntervalName.M60, IntervalName.DAY],
            "CRYPTO:GLOBAL:ETHUSD": [IntervalName.M15, IntervalName.M60, IntervalName.DAY]
        },
        "name":"multi_symbol_multi_timeframe",
            },

            {
                "item_data" : {
            "CRYPTO:GLOBAL:BTCUSD": [IntervalName.M15, IntervalName.M60, IntervalName.DAY],
        }
            },
            {
                "item_data" : {
            "CRYPTO:GLOBAL:ETHUSD": [IntervalName.M15],
        }
            },
         {
                "item_data" : {
            "CRYPTO:GLOBAL:SOLUSD": [IntervalName.M15],
                    "CRYPTO:GLOBAL:dogeUSD": [IntervalName.M15],
                    "CRYPTO:GLOBAL:xrbUSD": [IntervalName.M15],
        }
            },
        ]
        for req_data in data_list:
            result = FrontendRequest.call_sync(
                idt.backend_identity,
                idt.fun.ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM,
                **req_data,
                timeout=10  # 单位秒
            )
            logger.info(f"request result:{result}")
    @staticmethod
    def request_sub_topics_to_websocket_example():
        # refer to websocket_subscription_example.py
        result = FrontendRequest.call_sync(
            idt.backend_identity,
            idt.fun.SUBSCRIBE_OHLC_1M,
            "CRYPTO:GLOBAL:BTCUSD",
            "CRYPTO:GLOBAL:ETHUSD",
            timeout=10  # 单位秒
        )
        logger.info(f"request result:{result}")

    @staticmethod
    def request_history_ohlc_data_example():
        # refer to api_request_async_example.py or api_request_example.py
        params = {
            "schema_asset": SchemaAsset.CRYPTO,
            "country_symbol": "GLOBAL:BTCUSD",
            "interval": IntervalName.M60,
            "from_date": "2025-07-18T00:00:00+00:00",
            "to_date": "2025-10-05T23:59:59+00:00",
            "format": "json",
            "limit": 30
        }
        ohlcs = FrontendRequest.call_sync(
            idt.backend_identity,
            fun.OHLCS,
            **params,
            timeout=10 #10s
        )
        print(ApiListResultToFormatData2(ohlcs).get_polars())
    @staticmethod
    def request_latest_ohlc_data_example():
        # refer to api_request_async_example.py or api_request_example.py
        params = {
            "schema_asset": SchemaAsset.CRYPTO,
            "country_symbol": "GLOBAL:BTCUSD",
            "interval": IntervalName.M60,
            "limit": 30
        }
        ohlcs = FrontendRequest.call_sync(
            idt.backend_identity,
            fun.OHLCS_LATEST,
            **params,
            timeout=10 #10s
        )
        print(ApiListResultToFormatData2(ohlcs).get_polars())

    @staticmethod
    def subscribe_topics_example():
        #subscriber.add_topics(channel.OHLC,channel.NEWS,channel.EVENT)
        #or
        # my_first_sub_topic is from custom_pub_service_example.py
        subscriber.subscribe_topics("on_my_first_sub_topic")

        subscriber.subscribe_topics(*channel.get_array())





if __name__ == "__main__":
    subscriber = MyAsyncSubscriber()
    subscriber.run()
    #request ohlc from api
    #MyRequestTest.request_history_ohlc_data_example()
    #MyRequestTest.request_latest_ohlc_data_example()


    #subscribing topics
    MyRequestTest.subscribe_topics_example()

    #request subscribing topics via websocket
    #MyRequestTest.request_sub_topics_to_websocket_example()


    #multi_symbol_multi_timeframe.
    MyRequestTest.request_sub_multi_symbol_multi_timeframe_example()






    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("close...")