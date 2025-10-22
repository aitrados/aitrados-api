
from aitrados_api.trade_middleware.identity_mixin import *
class RpcFunction(RpcFunctionMixin):

    # OHLC related functions
    OHLCS_LATEST = "ohlc.a_ohlcs_latest" #DatasetClient sub function
    OHLCS = "ohlc.a_ohlcs" #DatasetClient sub function

    # Reference related functions (client.reference.xxx)
    REFERENCE = "reference.a_reference" #DatasetClient sub function
    SEARCH_OPTION = "reference.a_search_option" #DatasetClient sub function
    OPTIONS_EXPIRATION_DATE_LIST = "reference.a_options_expiration_date_list" #DatasetClient sub function
    STOCK_CORPORATE_ACTION_LIST = "reference.a_stock_corporate_action_list" #DatasetClient sub function

    # Economic related functions (client.economic.xxx)
    EVENT_CODES = "economic.a_event_codes" #DatasetClient sub function
    EVENT_LIST = "economic.a_event_list" #DatasetClient sub function
    EVENT = "economic.a_event" #DatasetClient sub function
    LATEST_EVENTS = "economic.a_latest_events" #DatasetClient sub function

    # Holiday related functions (client.holiday.xxx)
    HOLIDAY_LIST = "holiday.a_holiday_list" #DatasetClient sub function
    HOLIDAY_CODES = "holiday.a_holiday_codes" #DatasetClient sub function

    # News related functions (client.news.xxx)
    NEWS_LIST = "news.a_news_list" #DatasetClient sub function
    NEWS_LATEST = "news.a_news_latest" #DatasetClient sub function


    # Subscription
    SUBSCRIBE_NEWS = "a_subscribe_news" #WebSocketClient  sub function
    SUBSCRIBE_OHLC_1M = "a_subscribe_ohlc_1m" #WebSocketClient  sub function
    SUBSCRIBE_EVENT = "a_subscribe_event" #WebSocketClient  sub function

    UNSUBSCRIBE_NEWS = "a_unsubscribe_news" #WebSocketClient  sub function
    UNSUBSCRIBE_OHLC_1M = "a_unsubscribe_ohlc_1m" #WebSocketClient  sub function
    UNSUBSCRIBE_EVENT = "a_unsubscribe_event" #WebSocketClient  sub function


    RESUBSCRIBE_ALL = "resubscribe_all" #WebSocketClient  sub function
    ALL_SUBSCRIBED_TOPICS="a_get_all_subscribed_topics" #WebSocketClient  sub function

    # Chart OHLC
    ADD_LATEST_OHLC_CHART_FLOW_ITEM="add_latest_ohlc_chart_flow_item" #LatestOhlcChartFlowManager.add_item function
    REMOVE_LATEST_OHLC_CHART_FLOW_ITEM = "remove_latest_ohlc_chart_flow_item" #LatestOhlcChartFlowManager.remove_item function
    ADD_LATEST_OHLC_CHART_FLOW_ITEM_OR_GET_DATA="add_latest_ohlc_chart_flow_item_or_get_data" ##LatestOhlcChartFlowManager.add_item_or_get_data function



    # Multi-symbol multi-timeframe
    ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM="add_latest_ohlc_multi_timeframe_item"#LatestOhlcMultiTimeframeManager.add_item function
    REMOVE_LATEST_OHLC_MULTI_TIMEFRAME_ITEM = "remove_latest_ohlc_multi_timeframe_item"#LatestOhlcMultiTimeframeManager.remove_item function
    ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM_OR_GET_DATA = "add_latest_ohlc_multi_timeframe_item_or_get_data" ##LatestOhlcMultiTimeframeManager.add_item_or_get_data function




    # Client management functions
    #CLOSE = "close"




class Channel(ChannelMixin):
    #websockets msg
    NEWS = b"on_news"
    OHLC = b"on_ohlc"
    EVENT = b"on_event"
    AUTHENTICATE = b"on_show_subscribe"
    AUTH = b"on_authenticate"
    ERROR= b"on_error"
    HANDLE_MSG=b"on_handle_msg"
    #latest chart flow roll
    OHLC_CHART_FLOW_STREAMING = b"on_ohlc_chart_flow_streaming"
    # latest chart flow roll(multi symbol multi timeframe)
    MULTI_SYMBOL_MULTI_TIMEFRAME = b"on_multi_symbol_multi_timeframe"




class Identity(IdentityMixin):
    backend_identity = "aitrados_api"
    fun = RpcFunction
    channel = Channel

aitrados_api_identity=Identity