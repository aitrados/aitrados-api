import json

from aitrados_api.common_lib.common import get_real_intervals, get_fixed_full_symbol
from aitrados_api.common_lib.contant import IntervalName


class UniqueNameGenerator:
    @classmethod
    def get_original_name(self,item_data: dict, is_eth=False):
        item_data = self.get_new_item_data(item_data)


        data = {
            "item_data": item_data,
            "is_eth": is_eth
        }
        name = json.dumps(data)
        return name
    @classmethod
    def get_new_item_data(self, item_data: dict) -> dict:
        """
        Reorder item_data
        1. Sort dictionary keys consistently (lexicographic order)
        2. Sort interval list for each symbol according to IntervalName.get_array() order
        """


        if not item_data:
            raise ValueError(f"Error: Missing item_data")

        item_data=self.__get_fix_full_symbol_item_data(item_data)

        # 1. Sort dictionary keys (ensure order consistency)
        sorted_keys = sorted(item_data.keys())

        # 2. Get interval sorting order
        sort_order = IntervalName.get_array()
        sort_key_map = {interval: i for i, interval in enumerate(sort_order)}

        # 3. Build new sorted dictionary
        new_item_data = {}

        for key in sorted_keys:
            intervals = item_data[key]
            if not intervals:
                new_item_data[key] = []
                raise ValueError(f"Error:{key} Missing interval")
                #continue
            intervals=get_real_intervals(intervals)

            # Sort interval list
            sorted_intervals = sorted(
                intervals,
                key=lambda interval: sort_key_map.get(interval, len(sort_order))
            )

            new_item_data[key] = sorted_intervals

        return new_item_data

    @classmethod
    def __get_fix_full_symbol_item_data(self, item_data: dict) -> dict:
        """
        Convert all full_symbol keys in item_data to unified format
        """
        fixed_item_data = {}

        for full_symbol, intervals in item_data.items():
            fixed_item_data[get_fixed_full_symbol(full_symbol)] = intervals


        return fixed_item_data
