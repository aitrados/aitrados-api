
from threading import RLock
from typing import TYPE_CHECKING, Dict, List
import polars as pl
import pandas as pd

from aitrados_api.common_lib.any_list_data_to_format_data import deserialize_multi_symbol_multi_timeframe_data
from aitrados_api.latest_ohlc_multi_timeframe_alignment_flow.unique_name_generator import UniqueNameGenerator

from aitrados_api.universal_interface.callback_manage import CallbackManage




import asyncio

class TimeframeItemManager:
    _lock = RLock()

    data_map = {}
    name_original_name_map={}
    @classmethod
    async def aget_data_from_map(self, name=None, timeout=70,empty_data_result="Fetching data timeout: Failed to fetch data"):


        start_time = asyncio.get_event_loop().time()

        while True:
            # Use lock to safely read data
            with self._lock:

                if name not in self.data_map and name in self.name_original_name_map:
                    name=self.name_original_name_map

                if name in self.data_map and self.data_map[name] is not None:
                    return self.data_map[name]




            # Check if timeout occurred
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time >= timeout:
                raise TimeoutError(empty_data_result)

            # Wait 1 second before retry
            await asyncio.sleep(1)


    @classmethod
    def receive_data(self, data: Dict[str, List[str | list | pl.DataFrame | pd.DataFrame]], name, original_name):
        with self._lock:
            self.data_map[original_name]=data
            self.name_original_name_map[name]=name
        pass

    @classmethod
    def add_item(self, item_data: dict, is_eth=False,name=None,original_name=None):
        with self._lock:
            if not original_name:
                original_name=UniqueNameGenerator.get_original_name(item_data, is_eth)

            if original_name in self.data_map:
                return "subscribed"

            self.data_map[original_name]=None
            from aitrados_api.trade_middleware_service.trade_middleware_service_instance import \
                AitradosApiServiceInstance
            data=AitradosApiServiceInstance.latest_ohlc_multi_timeframe_manager.add_item(item_data=item_data,is_eth=is_eth,name=name,original_name=original_name)

            return data

    @classmethod
    async def add_item_or_get_data(self, item_data: Dict[str, List], is_eth=False, name: str = None, original_name=None
                             , rename_column_name_mapping: dict = None,
                             filter_column_names: List[str] = None,
                             limit: int = None, to_format=None
                             ):
        if not original_name:
            original_name = UniqueNameGenerator.get_original_name(item_data, is_eth)
        self.add_item(item_data=item_data,is_eth=is_eth,name=name,original_name=original_name)
        result=await self.aget_data_from_map(original_name)
        result=deserialize_multi_symbol_multi_timeframe_data(result,
                                                      rename_column_name_mapping=rename_column_name_mapping,
                                                      filter_column_names=filter_column_names,
                                                      limit=limit,
                                                      to_format=to_format

                                                      )

        return result


CallbackManage.add_custom_multi_timeframe_callback(TimeframeItemManager.receive_data)

