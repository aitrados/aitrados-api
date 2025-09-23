from typing import Callable, Dict, List
from aitrados_api.common_lib.contant import ChartDataFormat
from aitrados_api.common_lib.http_api.data_client import DatasetClient
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.latest_ohlc_chart_flow.latest_ohlc_chart_flow_manager import LatestOhlcChartFlowManager
from aitrados_api.latest_ohlc_multi_timeframe_alignment_flow.latest_ohlc_multi_timeframe_alignment import \
    LatestOhlcMultiTimeframeAlignment

import polars as pl


class LatestOhlcMultiTimeframeManager:
    def __init__(self,
                 api_client: DatasetClient,
                 ws_client: WebSocketClient,
                 multi_timeframe_callback: Callable,

                 limit=150,#data length limit
                 data_format=ChartDataFormat.POLARS,#multi_timeframe_callback return data format
                 works=10,# thread works number

                 ):
        self.latest_symbol_charting_manager = LatestOhlcChartFlowManager(
            latest_ohlc_chart_flow_callback=self._latest_ohlc_chart_flow_callback,
            api_client=api_client,
            ws_client=ws_client,
            limit=limit,
            data_format=ChartDataFormat.POLARS,
            works=works
        )

        self.alignments: Dict[str, LatestOhlcMultiTimeframeAlignment] = {}
        self.multi_timeframe_callback = multi_timeframe_callback
        self.data_format = data_format

        self.full_symbol_interval_name_map = {}  # {full_symbol:interval:set(name1,name2)}

    def _latest_ohlc_chart_flow_callback(self, df: pl.DataFrame):
        if df is None or df.is_empty():
            return

        try:
            asset_schema = df["asset_schema"][0]
            country_iso_code = df["country_iso_code"][0]
            symbol = df["symbol"][0]
            interval = df["interval"][0]

            full_symbol = f"{asset_schema}:{country_iso_code}:{symbol}".upper()

            names = self.full_symbol_interval_name_map.get(full_symbol, {}).get(interval, set())
            for name in names:
                alignment: LatestOhlcMultiTimeframeAlignment = self.alignments.get(name)
                alignment.receive_ohlc_data(df)

        except (pl.ColumnNotFoundError, IndexError) as e:
            print(f"Callback Error: Failed to process DataFrame. {e}")

    def add_item(self, item_data: Dict[str, List], name: str = "default", is_eth=False):
        """
        item_data={
            "CRYPTO:GLOBAL:BTCUSD":["15M","60M","DAY"],
            "CRYPTO:GLOBAL:BTCETH": ["15M", "60M", "DAY"]
        }
        """

        if name in self.alignments:
            return False
        self.alignments[name] = LatestOhlcMultiTimeframeAlignment(name=name,
                                                                  multi_timeframe_callback=self.multi_timeframe_callback,
                                                                  data_format=self.data_format,
                                                                  )
        for full_symbol, intervals in item_data.items():
            full_symbol = full_symbol.upper()
            intervals = [interval.upper() for interval in intervals]
            self.alignments[name].add_full_symbol(full_symbol, *intervals, is_eth=is_eth)

        for full_symbol, intervals in item_data.items():
            full_symbol = full_symbol.upper()
            intervals = [interval.upper() for interval in intervals]
            for interval in intervals:
                self.__add_update_map(full_symbol, interval, name)
                self.latest_symbol_charting_manager.add_item(full_symbol, interval, is_eth=is_eth)

    def remove_item(self, name: str = "default"):
        if not (alignment := self.alignments.get(name)):
            return

        full_symbols = list(alignment.timeframe_data.keys())
        delete_chart_items = []
        for full_symbol in full_symbols:

            if not (item := self.full_symbol_interval_name_map.get(full_symbol, {})):
                continue

            for interval in list(item.keys()):

                names = item[interval]
                is_eth = alignment.timeframe_data[full_symbol][interval]["is_eth"]

                if name in names:
                    names.discard(name)
                    if len(names) == 0:
                        del self.full_symbol_interval_name_map[full_symbol][interval]
                        if not self.full_symbol_interval_name_map[full_symbol]:
                            del self.full_symbol_interval_name_map[full_symbol]
                        delete_chart_items.append({
                            "full_symbol": full_symbol,
                            "interval": interval,
                            "is_eth": is_eth,
                        })

        for item in delete_chart_items:
            self.latest_symbol_charting_manager.remove_item(**item)
        del self.alignments[name]

    def __add_update_map(self, full_symbol, interval, name):
        if full_symbol not in self.full_symbol_interval_name_map:
            self.full_symbol_interval_name_map[full_symbol] = {}

        if interval not in self.full_symbol_interval_name_map[full_symbol]:
            self.full_symbol_interval_name_map[full_symbol][interval] = set()

        self.full_symbol_interval_name_map[full_symbol][interval].add(name)
