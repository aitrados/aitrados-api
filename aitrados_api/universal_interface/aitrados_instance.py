import os
from aitrados_api import SubscribeEndpoint, ChartDataFormat
from aitrados_api import ClientConfig
from aitrados_api import DatasetClient
from aitrados_api import WebSocketClient
from aitrados_api import LatestOhlcMultiTimeframeManager
from aitrados_api.common_lib.common import is_debug, get_env_value
from aitrados_api.universal_interface.callback_manage import CallbackManage
api_config = ClientConfig(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    debug=is_debug()
)
api_client_instance = DatasetClient(config=api_config)
ws_client_instance = WebSocketClient(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    is_reconnect=True,
    show_subscribe_handle_msg= CallbackManage._default_show_subscribe_handle_msg,
    handle_msg= CallbackManage._default_handle_msg,
    news_handle_msg= CallbackManage._default_news_handle_msg,
    event_handle_msg= CallbackManage._default_event_handle_msg,
    auth_handle_msg= CallbackManage._default_auth_handle_msg,
    endpoint=SubscribeEndpoint.REALTIME,
    debug=is_debug()
)
latest_ohlc_multi_timeframe_manager_instance = LatestOhlcMultiTimeframeManager(
    api_client=api_client_instance,
    ws_client=ws_client_instance,
    multi_timeframe_callback= CallbackManage._default_multi_timeframe_callback,
    limit=get_env_value("LIVE_STREAMING_OHLC_LIMIT", 150),  # data length limit
    works=10,
    data_format=ChartDataFormat.POLARS,  # multi_timeframe_callback return data format
    latest_ohlc_chart_flow_callback= CallbackManage._default_ohlc_chart_flow_streaming_callback
)
latest_symbol_charting_manager_instance=latest_ohlc_multi_timeframe_manager_instance.latest_symbol_charting_manager

