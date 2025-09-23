from datetime import time
from typing import Tuple, Optional

import polars as pl


def get_dominant_week_start_info(df: pl.DataFrame) -> Optional[Tuple[int, time]]:
    """
    分析历史DataFrame以找出主要的周开盘日和开盘时间。

    返回:
        一个包含主要星期几 (1=周一...7=周日) 和在该日最常见的
        开盘时间 (datetime.time) 的元组。如果无法确定则返回 None。
    """
    if df is None or df.height < 2:  # 需要至少几个数据点来寻找规律
        return None

    try:
        # 步骤 1: 找到主要的开盘星期
        weekday_counts = df['datetime'].dt.weekday().value_counts()
        if weekday_counts.is_empty():
            return None

        dominant_start_day = weekday_counts.sort(
            by=['count', 'datetime'], descending=[True, True]
        ).item(0, 'datetime')

        # 步骤 2: 筛选出主要开盘日的数据，并找到最常见的开盘时间
        df_dominant_day = df.filter(pl.col('datetime').dt.weekday() == dominant_start_day)

        if df_dominant_day.is_empty():
            return None  # 如果找到了主要星期，这里应该不会为空

        time_counts = df_dominant_day['datetime'].dt.time().value_counts()
        if time_counts.is_empty():
            return None

        dominant_start_time = time_counts.sort(
            by=['count', 'datetime'], descending=[True, True]
        ).item(0, 'datetime')

        return dominant_start_day, dominant_start_time

    except Exception:
        # 在任何异常情况下 (例如列不存在)，返回 None
        return None