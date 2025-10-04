from datetime import time
from typing import Tuple, Optional

import polars as pl


def get_dominant_week_start_info(df: pl.DataFrame) -> Optional[Tuple[int, time]]:
    """
    Analyze historical DataFrame to find the dominant week opening day and opening time.

    Returns:
        A tuple containing the dominant weekday (1=Monday...7=Sunday) and the most common
        opening time (datetime.time) on that day. Returns None if unable to determine.
    """
    if df is None or df.height < 2:  # Need at least a few data points to find patterns
        return None

    try:
        # Step 1: Find the dominant opening weekday
        weekday_counts = df['datetime'].dt.weekday().value_counts()
        if weekday_counts.is_empty():
            return None

        dominant_start_day = weekday_counts.sort(
            by=['count', 'datetime'], descending=[True, True]
        ).item(0, 'datetime')

        # Step 2: Filter data for the dominant opening day and find the most common opening time
        df_dominant_day = df.filter(pl.col('datetime').dt.weekday() == dominant_start_day)

        if df_dominant_day.is_empty():
            return None  # This shouldn't be empty if we found a dominant weekday

        time_counts = df_dominant_day['datetime'].dt.time().value_counts()
        if time_counts.is_empty():
            return None

        dominant_start_time = time_counts.sort(
            by=['count', 'datetime'], descending=[True, True]
        ).item(0, 'datetime')

        return dominant_start_day, dominant_start_time

    except Exception:
        # Return None in any exceptional case (e.g., column doesn't exist)
        return None