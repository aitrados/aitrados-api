import math
from datetime import datetime, timedelta
from typing import Dict

import polars as pl
from loguru import logger

from aitrados_api.common_lib.contant import IntervalName
from aitrados_api.latest_ohlc_chart_flow.ohlc_aggregation.ohlc_aggregation_utils import get_dominant_week_start_info


class OhlcAggregationMinute:
    def __init__(self, df: pl.DataFrame, data: Dict, limit=150):
        self.df = df
        self.data = data


        self.limit = limit
        self.interval = self.df.item(-1, "interval")
        self.is_aggregated = False

    def __aggregate_1m(self):
        last_timestamp = self.df.item(-1, "datetime")
        new_timestamp = self.data.get("datetime")
        if new_timestamp and new_timestamp > last_timestamp:

            new_row_df = pl.DataFrame([self.data], schema=self.df.schema)
            self.df = self.df.vstack(new_row_df).tail(self.limit)
            self.is_aggregated = True

    def __common_new_bar(self, new_bar_start_time: datetime):
        """通用内部函数：创建新的聚合K线。"""
        new_bar_data = self.data.copy()
        new_bar_data["datetime"] = new_bar_start_time
        new_bar_data["interval"] = self.interval
        new_bar_data["vwap"] = new_bar_data["close"]

        new_row_df = pl.DataFrame([new_bar_data], schema=self.df.schema)
        self.df = self.df.vstack(new_row_df).tail(self.limit)
        self.is_aggregated = True

    def __common_update_bar(self):
        """通用内部函数：更新最后一根未收盘的K线。"""
        last_bar = self.df[-1, :]
        df_without_last = self.df[:-1]
        last_bar_dict = last_bar.to_dicts()[0]

        last_bar_dict["high"] = max(last_bar_dict["high"], self.data["high"])
        last_bar_dict["low"] = min(last_bar_dict["low"], self.data["low"])
        last_bar_dict["close"] = self.data["close"]
        last_bar_dict["volume"] += self.data["volume"]
        last_bar_dict["close_datetime"] = self.data["close_datetime"]  # 直接使用 datetime 对象

        updated_last_row_df = pl.DataFrame([last_bar_dict], schema=self.df.schema)
        self.df = pl.concat([df_without_last, updated_last_row_df])
        self.is_aggregated = True

    def __aggregate_common_interval(self):
        """通用聚合函数，用于将1分钟数据流合并为任意分钟周期（例如3M, 5M, 10M）。"""
        minutes = int(self.interval[:-1])

        last_bar = self.df[-1, :]
        last_bar_open_time = last_bar.item(0, "datetime")  # 直接获取 datetime 对象
        last_bar_close_time = last_bar.item(0, "close_datetime") # 直接获取 datetime 对象
        new_1m_bar_open_time = self.data["datetime"]  # 直接获取 datetime 对象

        if new_1m_bar_open_time < last_bar_close_time:
            return

        new_bar_minute = new_1m_bar_open_time.minute - (new_1m_bar_open_time.minute % minutes)
        new_bar_start_time = new_1m_bar_open_time.replace(minute=new_bar_minute, second=0, microsecond=0)

        if new_bar_start_time > last_bar_open_time:
            self.__common_new_bar(new_bar_start_time)
        else:
            self.__common_update_bar()

    def __aggregate_common_interval_for_large_minute(self):
        """
        为大周期（>=60分钟）设计的聚合函数。
        通过分析相对于当前数据点最近15天的历史数据中“重复出现的开盘时间规律”，
        来精确判断新K线的开启时刻。此方法能有效规避长假等影响，并完全适用于历史回测。
        """
        new_1m_bar_open_time = self.data["datetime"]

        # --- 步骤 1: 从相对于当前数据点的最近15天历史中，找出“重复出现”的开盘时间点 ---
        historical_anchor_times = set()
        try:
            start_date_filter = new_1m_bar_open_time - pl.duration(days=15)
            recent_df = self.df.filter(pl.col("datetime") > start_date_filter)

            if recent_df.is_empty():
                logger.debug(
                    f"No recent data in the last 15 days to determine anchor times. Falling back to default.")
                return self.__aggregate_common_interval()


            # Bug修复：在value_counts()前使用.alias()给时间列一个确定的名称 "anchor_time"
            anchor_time_counts = recent_df.get_column("datetime").dt.time().alias("anchor_time").value_counts()

            # 只选择那些出现次数大于1的时间点
            # 使用我们刚刚设置的别名"anchor_time"来安全地获取列
            proven_anchor_times = anchor_time_counts.filter(
                pl.col("count") > 1
            ).get_column("anchor_time")

            if not proven_anchor_times.is_empty():
                historical_anchor_times = set(proven_anchor_times)

        except Exception as e:
            logger.warning(
                f"Could not build historical anchor times from recent data due to: {e}. Falling back to default.")
            self.__aggregate_common_interval()
            return

        if not historical_anchor_times:
            logger.debug(
                f"No recurring historical anchor time pattern found in the last 15 days. Falling back to default.")
            self.__aggregate_common_interval()
            return

        # --- 步骤 2: 使用找到的“可靠锚点”来判断新K线的归属 ---
        last_bar = self.df[-1, :]
        last_bar_open_time = last_bar.item(0, "datetime")

        is_new_bar_time = new_1m_bar_open_time.time() in historical_anchor_times

        if is_new_bar_time and new_1m_bar_open_time > last_bar_open_time:
            self.__common_new_bar(new_1m_bar_open_time)
        else:
            self.__common_update_bar()





    def __aggregate_common_interval_for_week(self):
        """
        将1分钟数据聚合为周线bar，动态确定周的起始日和时间，使其对假期和不规则日程具有鲁棒性。
        """
        # 步骤 1: 从历史数据中获取主要的开盘日和时间。
        start_info = get_dominant_week_start_info(self.df)
        new_1m_bar_open_time = self.data["datetime"]

        if not start_info:
            # 当没有足够历史来确定规律时的后备方案。
            # 检查ISO周数是否已更改。虽然不够完美，但优于无操作。
            last_bar_open_time = self.df.item(-1, "datetime")
            if new_1m_bar_open_time.isocalendar().week != last_bar_open_time.isocalendar().week:
                self.__common_new_bar(new_1m_bar_open_time)
            else:
                self.__common_update_bar()
            return

        dominant_weekday, dominant_start_time = start_info
        last_bar_open_time = self.df.item(-1, "datetime")

        # 步骤 2: 确定下一个周线bar的预期开始时间。
        # 从上一个bar的日期开始，找到匹配主要开盘日的下一个日期。
        # Polars: weekday() is 1-7 for Mon-Sun. Python: weekday() is 0-6 for Mon-Sun.
        last_bar_date = last_bar_open_time.date()
        days_ahead = (dominant_weekday - 1 - last_bar_date.weekday() + 7) % 7
        if days_ahead == 0:  # 如果今天是主要开盘日，则寻找下一周的。
            days_ahead = 7

        next_dominant_day_date = last_bar_date + timedelta(days=days_ahead)

        # 结合日期和时间，得到精确的预期开始时间戳。
        # 假设与上一个bar使用相同的时区。
        expected_next_bar_start_time = datetime.combine(
            next_dominant_day_date,
            dominant_start_time,
            tzinfo=last_bar_open_time.tzinfo
        )

        # 步骤 3: 比较并决策。
        if new_1m_bar_open_time >= expected_next_bar_start_time:
            # 新数据处于或晚于新一周交易的预期开始时间。
            # 这个新bar的开始时间就是我们为它看到的第一个tick的时间。
            self.__common_new_bar(new_1m_bar_open_time)
        else:
            # 新数据仍属于当前周的交易时段。
            self.__common_update_bar()


    def __aggregate_common_interval_for_mon(self):
        """
        将1分钟数据聚合为月线bar。
        """
        # 步骤 1: 获取时间戳
        last_bar_open_time = self.df.item(-1, "datetime")
        new_1m_bar_open_time = self.data["datetime"]

        # 步骤 2: 如果新数据的月份晚于最后K线的月份，则创建新的bar。
        is_new_month = (new_1m_bar_open_time.year > last_bar_open_time.year) or \
                       (new_1m_bar_open_time.year == last_bar_open_time.year and
                        new_1m_bar_open_time.month > last_bar_open_time.month)

        if is_new_month:
            # 新bar的起始时间是该新月的第一个tick的时间戳。
            self.__common_new_bar(new_1m_bar_open_time)
        else:
            self.__common_update_bar()


    def aggregate(self):
        if self.interval == IntervalName.M1:
            self.__aggregate_1m()
        elif self.interval in [IntervalName.M1, IntervalName.M3, IntervalName.M5, IntervalName.M10, IntervalName.M15,IntervalName.M30]:
            self.__aggregate_common_interval()
        elif self.interval in [ IntervalName.M60, IntervalName.M120, IntervalName.M240,IntervalName.DAY]:
            self.__aggregate_common_interval_for_large_minute()
        elif self.interval in [IntervalName.WEEK]:
            self.__aggregate_common_interval_for_week()
        elif self.interval in [IntervalName.MON]:
            self.__aggregate_common_interval_for_mon()


        if self.is_aggregated:
            return self.df
        else:
            return None