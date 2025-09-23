import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import sleep
from typing import Callable, List, Dict

from aitrados_api.common_lib.contant import ChartDataFormat
from aitrados_api.common_lib.http_api.data_client import DatasetClient
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.latest_ohlc_chart_flow.latest_ohlc_chart_flow import LatestOhlcChartFlow


class LatestOhlcChartFlowManager:
    def __init__(self,
                 api_client: DatasetClient,
                 latest_ohlc_chart_flow_callback: Callable,
                 ws_client: WebSocketClient,
                 limit=150,
                 data_format=ChartDataFormat.POLARS,
                 works=10,
                 ):

        ws_client.ohlc_handle_msg = self.subscribe_ohlc_handle_msg
        self.api_client = api_client
        self.latest_ohlc_chart_flow_callback = latest_ohlc_chart_flow_callback
        self.ws_client = ws_client
        self.limit = limit
        self.data_format = data_format
        self.works = works
        self.executor = ThreadPoolExecutor(max_workers=self.works)

        self.symbol_charting_list: Dict[str, Dict[tuple[str, bool], LatestOhlcChartFlow]] = {}
        self.submitting_subscription_topics = set()
        self._lock = threading.RLock()

    def _subscribe(self, full_symbol):
        if full_symbol in self.submitting_subscription_topics:
            return True

        self.submitting_subscription_topics.add(full_symbol)
        if self.ws_client.check_subscription_topic("ohlc", full_symbol):
            return True
        while True:
            if self.ws_client.authorized:
                self.ws_client.subscribe_ohlc_1m(
                    full_symbol,
                )
                return True
            print("Waiting for Aitrados WebSocket authorization...")
            sleep(2)

    def add_item(self, full_symbol, interval, is_eth=False):
        #is_eth: US stock extended hour
        with self._lock:
            full_symbol = full_symbol.upper()
            interval = interval.upper()
            if full_symbol not in self.symbol_charting_list:
                self.symbol_charting_list[full_symbol] = {}
            if (interval, is_eth) in self.symbol_charting_list[full_symbol]:
                return True
            self.symbol_charting_list[full_symbol][(interval, is_eth)] = symbol_charting = LatestOhlcChartFlow(
                full_symbol=full_symbol,
                interval=interval,
                api_client=self.api_client,
                latest_ohlc_chart_flow_callback=self.latest_ohlc_chart_flow_callback,
                limit=self.limit,
                is_eth=is_eth,
                data_format=self.data_format

            )
            data = symbol_charting.run()
            if data is not None:
                threading.Thread(target=self._subscribe, kwargs={"full_symbol": full_symbol}).start()

            return True

    def remove_item(self, full_symbol, interval, is_eth=False):
        with self._lock:
            full_symbol = full_symbol.upper()
            interval = interval.upper()
            if full_symbol not in self.symbol_charting_list:
                return True
            if (interval, is_eth) not in self.symbol_charting_list[full_symbol]:
                return True
            del self.symbol_charting_list[full_symbol][(interval, is_eth)]
            if len(self.symbol_charting_list[full_symbol]) == 0:
                del self.symbol_charting_list[full_symbol]
                if self.ws_client.check_subscription_topic("ohlc", full_symbol):
                    self.ws_client.unsubscribe_ohlc_1m(full_symbol)
                self.submitting_subscription_topics.discard(full_symbol)
                # print(f"Removed subscription for symbol '{full_symbol}' (interval: {interval}, is_eth: {is_eth})")
            return True

    def _process_subscribe_data_item(self, data: Dict):
        """Processes a single data item from the websocket stream."""

        if not data:
            return
        del data["trading_session"]


        if isinstance(data.get("datetime"), str):
            data['datetime'] = datetime.fromisoformat(data['datetime'])
        if isinstance(data.get("close_datetime"), str):
            data['close_datetime'] = datetime.fromisoformat(data['close_datetime'])

        full_symbol = f"{data.get('asset_schema', '')}:{data.get('country_iso_code', '')}:{data.get('symbol', '')}".upper()
        if root_node := self.symbol_charting_list.get(full_symbol):
            for symbol_charting in list(root_node.values()):
                pass
                symbol_charting.receive_subscribe_ohlc_data_1m(data)
                pass
        pass

    def subscribe_ohlc_handle_msg(self, client: WebSocketClient, data_list):
        self.push_subscribe_ohlc_data(data_list)

    def push_subscribe_ohlc_data(self, data_list: List[Dict]):
        """
[
  {
    "asset_schema": "crypto",
    "country_iso_code": "GLOBAL",
    "exchange": "GLOBAL",
    "symbol": "BTCUSD",
    "datetime": "2025-09-20T03:01:00+00:00",
    "close_datetime": "2025-09-20T03:02:00+00:00",
    "open": 115664.02,
    "high": 115800,
    "low": 115561.2,
    "close": 115647.76,
    "volume": 1.01338878,
    "trading_session": "RTH",
    "interval": "1M",
    "vwap": 77120.73779626
  }
]
        """
        if not data_list:
            return

        self.executor.map(self._process_subscribe_data_item, data_list)
