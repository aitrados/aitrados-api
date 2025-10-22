import threading
from typing import Dict, List
from threading import RLock

import pandas as pd

from aitrados_api.common_lib.common import get_full_symbol, to_format_data
from aitrados_api.common_lib.contant import IntervalName, ChartDataFormat

import polars as pl

from aitrados_api.common_lib.response_format import WsUnifiedResponse
from aitrados_api.latest_ohlc_chart_flow.latest_ohlc_chart_flow_manager import LatestOhlcChartFlowManager
from aitrados_api.trade_middleware.publisher import async_publisher_instance


class LatestOhlcMultiTimeframeAlignment:

    def __init__(self,
                 multi_timeframe_callback: callable,
                 latest_symbol_charting_manager: LatestOhlcChartFlowManager,
                 original_name: str,
                 name: str = None,
                 data_format=ChartDataFormat.POLARS,

                 ):
        self.multi_timeframe_callback = multi_timeframe_callback
        self.latest_symbol_charting_manager = latest_symbol_charting_manager
        self.data_format = data_format
        self.original_name = original_name
        self.name = name if name else self.original_name
        self.timeframe_data: Dict[str, Dict[str, dict]] = {}
        self.__last_push_datatime = None



        self._lock = RLock()

    def resort_timeframes(self, full_symbol: str) -> bool:
        with self._lock:
            full_symbol = full_symbol.upper()
            if full_symbol not in self.timeframe_data:
                return False

            intervals_dict = self.timeframe_data.get(full_symbol)
            if not intervals_dict:
                return True  # No intervals to sort

            # Get the standard sort array from IntervalName
            sort_order = IntervalName.get_array()

            # Create an interval -> index map for efficient lookup of sort position
            sort_key_map = {interval: i for i, interval in enumerate(sort_order)}

            # Sort the dictionary entries based on the index in sort_key_map
            # If an interval is not in sort_key_map, put it at the end
            sorted_items = sorted(
                intervals_dict.items(),
                key=lambda item: sort_key_map.get(item[0], len(sort_order))
            )

            # Create a new dictionary from the sorted items to ensure order
            self.timeframe_data[full_symbol] = dict(sorted_items)

            return True

    def add_full_symbol(self, full_symbol, *intervals, is_eth=False):
        with self._lock:
            if len(intervals) == 0:
                return False

            full_symbol = full_symbol.upper()

            if full_symbol not in self.timeframe_data:
                self.timeframe_data[full_symbol] = {}
            for interval in intervals:
                interval = interval.upper()
                if not IntervalName.is_in_array(interval):
                    continue
                if interval not in self.timeframe_data[full_symbol]:
                    self.timeframe_data[full_symbol][interval] = {"is_eth": is_eth}
            self.resort_timeframes(full_symbol)
            threading.Thread(target=self.__init_cache_data).start()
            return True

    def __init_cache_data(self):
        with self._lock:
            for full_symbol, items in self.timeframe_data.items():
                for interval, info in items.items():
                    is_eth = info["is_eth"]
                    if "df" in info:
                        continue
                    try:
                        obj = self.latest_symbol_charting_manager.symbol_charting_list[full_symbol][(interval, is_eth)]
                        if obj.df is not None and len(obj.df) > 0:
                            self.receive_ohlc_data(obj.df.clone())
                    except Exception as e:

                        pass

        pass

    def __is_multi_symbol_multi_timeframe_align(self) -> bool:
        """
        Implements a global time alignment check.
        Checks whether all symbols and timeframes tracked in this alignment instance have received data,
        and whether their 'last_close_datetime' are all aligned to the same point in time.
        """
        # Do not push if no data is being tracked at all
        if not self.timeframe_data:
            return False

        all_datetimes = []
        # 1. Collect the last_close_datetime of all timeframes for all full_symbols tracked by this instance
        for intervals_dict in self.timeframe_data.values():
            if not intervals_dict:
                # If a symbol unexpectedly has no timeframes, the data is considered incomplete
                return False
            for info in intervals_dict.values():
                all_datetimes.append(info.get('last_close_datetime'))

        # If the collected list of times is empty (which should not happen unless there are no intervals under any symbol), do not push
        if not all_datetimes:
            return False

        # 2. Check 1: Whether all timeframes have received data (none are None)
        if any(dt is None for dt in all_datetimes):
            return False

        # 3. Check 2: Put all time points into a set. If the set size is > 1, it means the time points are not aligned
        if len(set(all_datetimes)) > 1:
            return False
        # 4. Check 3: Prevent pushing duplicate data for the same time point
        if self.__last_push_datatime and all_datetimes[0] == self.__last_push_datatime:
            return False
        # All checks passed, global alignment is complete
        return True

    def __get_pushed_data(self) -> Dict[str, List[str | list | pl.DataFrame | pd.DataFrame]] | None:
        with self._lock:
            # First, check if all data is aligned and ready
            if not self.__is_multi_symbol_multi_timeframe_align():
                return None

            result = {}
            # Iterate over each full_symbol
            for full_symbol, intervals_dict in self.timeframe_data.items():
                # The resort_timeframes method has ensured that intervals_dict is sorted internally by timeframe
                data_list = []
                # Iterate over the data of all timeframes under this symbol
                for info in intervals_dict.values():
                    # __is_multi_symbol_multi_timeframe_align() ensures that 'df' must exist at this time
                    df = info.get('df')
                    if df is not None:
                        # Convert the DataFrame to the format specified during initialization
                        formatted_data = to_format_data(df, self.data_format)
                        data_list.append(formatted_data)

                result[full_symbol] = data_list

            return result


    def receive_ohlc_data(self, df: pl.DataFrame):
        full_symbol = get_full_symbol(df)
        interval = df["interval"][0]
        interval = interval.upper()
        last_close_datetime = df["close_datetime"][-1]
        is_updated = False

        with self._lock:
            try:
                info = self.timeframe_data[full_symbol][interval]
                info["df"] = df
                info["last_close_datetime"] = last_close_datetime
                is_updated = True
            except KeyError:
                pass

        if not is_updated:
            return

        push_data = self.__get_pushed_data()
        if not push_data:
            return
        self.multi_timeframe_callback(name=self.name, data=push_data, original_name=self.original_name)
        self._trade_middleware_publish(push_data)

    def _trade_middleware_publish(self, push_data: dict):
        new_push_data = {}
        for full_symbol, data_list in push_data.items():
            converted_data_list = []

            for data in data_list:
                if not isinstance(data, str | dict | list):
                    converted_data = to_format_data(data, ChartDataFormat.CSV)
                    converted_data_list.append(converted_data)
                else:
                    converted_data_list.append(data)

            new_push_data[full_symbol] = converted_data_list

        result = {
            "name": self.name,
            "original_name": self.original_name,
            "data": new_push_data

        }

        handle_msg = WsUnifiedResponse(message_type="multi_symbol_multi_timeframe",
                                       result=result).model_dump_json()
        async_publisher_instance.send_topic("on_multi_symbol_multi_timeframe", result)
        async_publisher_instance.send_topic("on_handle_msg", handle_msg)
