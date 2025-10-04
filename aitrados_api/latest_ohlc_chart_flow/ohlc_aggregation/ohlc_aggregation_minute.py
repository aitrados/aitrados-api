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
        """Common internal function: Create a new aggregated K-line bar."""
        new_bar_data = self.data.copy()
        new_bar_data["datetime"] = new_bar_start_time
        new_bar_data["interval"] = self.interval
        new_bar_data["vwap"] = new_bar_data["close"]

        new_row_df = pl.DataFrame([new_bar_data], schema=self.df.schema)
        self.df = self.df.vstack(new_row_df).tail(self.limit)
        self.is_aggregated = True

    def __common_update_bar(self):
        """Common internal function: Update the last unclosed K-line bar."""
        last_bar = self.df[-1, :]
        df_without_last = self.df[:-1]
        last_bar_dict = last_bar.to_dicts()[0]

        last_bar_dict["high"] = max(last_bar_dict["high"], self.data["high"])
        last_bar_dict["low"] = min(last_bar_dict["low"], self.data["low"])
        last_bar_dict["close"] = self.data["close"]
        last_bar_dict["volume"] += self.data["volume"]
        last_bar_dict["close_datetime"] = self.data["close_datetime"]  # Use datetime object directly

        updated_last_row_df = pl.DataFrame([last_bar_dict], schema=self.df.schema)
        self.df = pl.concat([df_without_last, updated_last_row_df])
        self.is_aggregated = True

    def __aggregate_common_interval(self):
        """Common aggregation function for merging 1-minute data streams into arbitrary minute intervals (e.g., 3M, 5M, 10M)."""
        minutes = int(self.interval[:-1])

        last_bar = self.df[-1, :]
        last_bar_open_time = last_bar.item(0, "datetime")  # Get datetime object directly
        last_bar_close_time = last_bar.item(0, "close_datetime") # Get datetime object directly
        new_1m_bar_open_time = self.data["datetime"]  # Get datetime object directly

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
        Aggregation function designed for large intervals (>=60 minutes).
        By analyzing "recurring opening time patterns" from the last 15 days of historical data
        relative to the current data point, it accurately determines when new K-line bars should start.
        This method effectively avoids the impact of long holidays and is fully applicable to historical backtesting.
        """
        new_1m_bar_open_time = self.data["datetime"]

        # --- Step 1: Find "recurring" opening time points from the last 15 days of historical data relative to the current data point ---
        historical_anchor_times = set()
        try:
            start_date_filter = new_1m_bar_open_time - pl.duration(days=15)
            recent_df = self.df.filter(pl.col("datetime") > start_date_filter)

            if recent_df.is_empty():
                logger.debug(
                    f"No recent data in the last 15 days to determine anchor times. Falling back to default.")
                return self.__aggregate_common_interval()


            # Bug fix: Use .alias() to give the time column a definite name "anchor_time" before value_counts()
            anchor_time_counts = recent_df.get_column("datetime").dt.time().alias("anchor_time").value_counts()

            # Select only time points that appear more than once
            # Use the alias "anchor_time" we just set to safely get the column
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

        # --- Step 2: Use the found "reliable anchor points" to determine the attribution of new K-line bars ---
        last_bar = self.df[-1, :]
        last_bar_open_time = last_bar.item(0, "datetime")

        is_new_bar_time = new_1m_bar_open_time.time() in historical_anchor_times

        if is_new_bar_time and new_1m_bar_open_time > last_bar_open_time:
            self.__common_new_bar(new_1m_bar_open_time)
        else:
            self.__common_update_bar()





    def __aggregate_common_interval_for_week(self):
        """
        Aggregate 1-minute data into weekly bars, dynamically determining the start day and time of the week
        to make it robust against holidays and irregular schedules.
        """
        # Step 1: Get the dominant opening day and time from historical data.
        start_info = get_dominant_week_start_info(self.df)
        new_1m_bar_open_time = self.data["datetime"]

        if not start_info:
            # Fallback when there's insufficient history to determine the pattern.
            # Check if the ISO week number has changed. Not perfect, but better than no action.
            last_bar_open_time = self.df.item(-1, "datetime")
            if new_1m_bar_open_time.isocalendar().week != last_bar_open_time.isocalendar().week:
                self.__common_new_bar(new_1m_bar_open_time)
            else:
                self.__common_update_bar()
            return

        dominant_weekday, dominant_start_time = start_info
        last_bar_open_time = self.df.item(-1, "datetime")

        # Step 2: Determine the expected start time of the next weekly bar.
        # Starting from the last bar's date, find the next date that matches the dominant opening day.
        # Polars: weekday() is 1-7 for Mon-Sun. Python: weekday() is 0-6 for Mon-Sun.
        last_bar_date = last_bar_open_time.date()
        days_ahead = (dominant_weekday - 1 - last_bar_date.weekday() + 7) % 7
        if days_ahead == 0:  # If today is the dominant opening day, look for next week's.
            days_ahead = 7

        next_dominant_day_date = last_bar_date + timedelta(days=days_ahead)

        # Combine date and time to get the precise expected start timestamp.
        # Assume the same timezone as the previous bar.
        expected_next_bar_start_time = datetime.combine(
            next_dominant_day_date,
            dominant_start_time,
            tzinfo=last_bar_open_time.tzinfo
        )

        # Step 3: Compare and make decision.
        if new_1m_bar_open_time >= expected_next_bar_start_time:
            # New data is at or after the expected start time of a new week's trading.
            # The start time of this new bar is the time of the first tick we see for it.
            self.__common_new_bar(new_1m_bar_open_time)
        else:
            # New data still belongs to the current week's trading session.
            self.__common_update_bar()


    def __aggregate_common_interval_for_mon(self):
        """
        Aggregate 1-minute data into monthly bars.
        """
        # Step 1: Get timestamps
        last_bar_open_time = self.df.item(-1, "datetime")
        new_1m_bar_open_time = self.data["datetime"]

        # Step 2: If the new data's month is later than the last K-line's month, create a new bar.
        is_new_month = (new_1m_bar_open_time.year > last_bar_open_time.year) or \
                       (new_1m_bar_open_time.year == last_bar_open_time.year and
                        new_1m_bar_open_time.month > last_bar_open_time.month)

        if is_new_month:
            # The start time of the new bar is the timestamp of the first tick in that new month.
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