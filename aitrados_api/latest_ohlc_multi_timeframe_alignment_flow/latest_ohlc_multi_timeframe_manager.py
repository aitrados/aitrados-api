import threading
from copy import deepcopy
from typing import Callable, Dict, List

from loguru import logger

from aitrados_api.common_lib.contant import ChartDataFormat
from aitrados_api.common_lib.http_api.data_client import DatasetClient
from aitrados_api.common_lib.response_format import ErrorResponse, UnifiedResponse
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.latest_ohlc_chart_flow.latest_ohlc_chart_flow_manager import LatestOhlcChartFlowManager
from aitrados_api.latest_ohlc_multi_timeframe_alignment_flow.latest_ohlc_multi_timeframe_alignment import \
    LatestOhlcMultiTimeframeAlignment

import polars as pl

from aitrados_api.latest_ohlc_multi_timeframe_alignment_flow.unique_name_generator import UniqueNameGenerator
from aitrados_api.universal_interface.timeframe_item_management import TimeframeItemManager


class LatestOhlcMultiTimeframeManager:
    def __init__(self,
                 api_client: DatasetClient,
                 ws_client: WebSocketClient,
                 multi_timeframe_callback: Callable,

                 limit=150,#data length limit
                 data_format=ChartDataFormat.POLARS,#multi_timeframe_callback return data format
                 works=10,# thread works number
                 ohlc_handle_msg: Callable = None, #reserve WebSocketClient ohlc callback
                 latest_ohlc_chart_flow_callback: Callable = None #reserve LatestOhlcChartFlowManager streaming ohlc callback
                 ):
        self.latest_symbol_charting_manager = LatestOhlcChartFlowManager(
            latest_ohlc_chart_flow_callback=self._latest_ohlc_chart_flow_callback,
            api_client=api_client,
            ws_client=ws_client,
            limit=limit,
            data_format=ChartDataFormat.POLARS,
            works=works,

            ohlc_handle_msg=ohlc_handle_msg
        )
        self.latest_ohlc_chart_flow_callback = latest_ohlc_chart_flow_callback

        self.alignments: Dict[str, LatestOhlcMultiTimeframeAlignment] = {}
        self.multi_timeframe_callback = multi_timeframe_callback
        self.data_format = data_format

        self.full_symbol_interval_name_map = {}  # {full_symbol:interval:set(name1,name2)}

        self.name_original_name_map={}  #custom_name  mapping original_name
        self._lock = threading.RLock()
        from aitrados_api.trade_middleware_service.trade_middleware_service_instance import AitradosApiServiceInstance
        AitradosApiServiceInstance.latest_ohlc_multi_timeframe_manager = self
    def _latest_ohlc_chart_flow_callback(self, data: pl.DataFrame,full_symbol: str, interval: str,**kwargs):
        if data is None or data.is_empty():
            return

        try:
            #asset_schema = df["asset_schema"][0]
            #country_iso_code = df["country_iso_code"][0]
            #symbol = df["symbol"][0]
            #interval = df["interval"][0]

            #full_symbol = f"{asset_schema}:{country_iso_code}:{symbol}".upper()

            names = self.full_symbol_interval_name_map.get(full_symbol, {}).get(interval, set())
            for name in names:
                alignment: LatestOhlcMultiTimeframeAlignment = self.alignments.get(name)
                alignment.receive_ohlc_data(data)

        except (pl.ColumnNotFoundError, IndexError) as e:
            print(f"Callback Error: Failed to process DataFrame. {e}")
        if self.latest_ohlc_chart_flow_callback:
            self.latest_ohlc_chart_flow_callback(data.clone())




    def add_item_in_background(self, item_data: Dict[str, List], is_eth=False, name: str = None, original_name=None):
        kwargs={
            "item_data": item_data,
            "is_eth": is_eth,
            "name": name,
            "original_name": original_name
        }
        threading.Thread(target=self.add_item, kwargs=kwargs,daemon=True).start()
        return True

    def add_item(self, item_data: Dict[str, List], is_eth=False,name: str = None, original_name=None):
        """
        item_data={
            "CRYPTO:GLOBAL:BTCUSD":["15M","60M","DAY"],
            "CRYPTO:GLOBAL:BTCETH": ["15M", "60M", "DAY"]
        }
        """
        if not original_name:
            try:
                original_name=UniqueNameGenerator.get_original_name(item_data,is_eth)
            except Exception as e:
                logger.warning(f"Generate original_name error:{e}")
                return ErrorResponse(message=f"Generate original_name error:{e}")


        if not name:
            name=original_name



        if original_name in self.alignments:
            #ralate custom_name

            if  name not in self.name_original_name_map:
                self.name_original_name_map[name] = original_name
            return UnifiedResponse(result={"name": name, "original_name": original_name})
        self.alignments[original_name] = LatestOhlcMultiTimeframeAlignment(name=name,
                                                                  multi_timeframe_callback=self.multi_timeframe_callback,
                                                                  original_name=original_name,
                                                                  data_format=self.data_format,
                                                                  latest_symbol_charting_manager=self.latest_symbol_charting_manager
                                                                  )
        for full_symbol, intervals in item_data.items():
            full_symbol = full_symbol.upper()
            intervals = [interval.upper() for interval in intervals]
            self.alignments[original_name].add_full_symbol(full_symbol, *intervals, is_eth=is_eth)
            self.name_original_name_map[name] = original_name

        for full_symbol, intervals in item_data.items():
            full_symbol = full_symbol.upper()
            intervals = [interval.upper() for interval in intervals]
            for interval in intervals:
                self.__add_update_map(full_symbol, interval, original_name)
                result=self.latest_symbol_charting_manager.add_item(full_symbol, interval, is_eth=is_eth)
                if isinstance(result, ErrorResponse):
                    threading.Thread(target=self.remove_item, kwargs={"name": original_name},daemon=True).start()
                    return result
        return UnifiedResponse(result={"name": name, "original_name": original_name})

    def remove_item(self, name: str):
        with self._lock:

            if name  in self.name_original_name_map:
                name=deepcopy(self.name_original_name_map[name])
                del self.name_original_name_map[name]

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

    @classmethod
    async def add_item_or_get_data(cls, item_data: Dict[str, List], is_eth=False, name: str = None, original_name=None
                                   , rename_column_name_mapping: dict = None,
                                   filter_column_names: List[str] = None,
                                   limit: int = None, to_format=None
                                   ):
        return await TimeframeItemManager.add_item_or_get_data(
            item_data=item_data,
            is_eth=is_eth,
            name=name,
            original_name=original_name,
            rename_column_name_mapping=rename_column_name_mapping,
            filter_column_names=filter_column_names,
            limit=limit,
            to_format=to_format
        )

