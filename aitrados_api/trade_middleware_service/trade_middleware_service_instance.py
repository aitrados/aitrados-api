import os
import time

from aitrados_api.common_lib.http_api.config import ClientConfig
from aitrados_api.common_lib.http_api.data_client import DatasetClient
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.latest_ohlc_chart_flow.latest_ohlc_chart_flow_manager import LatestOhlcChartFlowManager
from aitrados_api.latest_ohlc_multi_timeframe_alignment_flow.latest_ohlc_multi_timeframe_manager import \
    LatestOhlcMultiTimeframeManager


class AitradosApiServiceInstance:
    #TradeMiddleware's external services should be shared with others to improve efficiency and save costs
    api_client: DatasetClient = None
    ws_client: WebSocketClient = None
    latest_ohlc_chart_flow_manager:LatestOhlcChartFlowManager = None
    latest_ohlc_multi_timeframe_manager:LatestOhlcMultiTimeframeManager = None

