from datetime import datetime, timezone
import io

from typing import Callable, Dict
from loguru import logger

from aitrados_api.common_lib.common import to_format_data
from aitrados_api.common_lib.contant import ChartDataFormat, IntervalName
from aitrados_api.common_lib.http_api.data_client import DatasetClient
import polars as pl

from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse
from aitrados_api.latest_ohlc_chart_flow.ohlc_aggregation.ohlc_aggregation_minute import OhlcAggregationMinute


class LatestOhlcChartFlow:
    def __init__(self, full_symbol,
                 interval,
                 api_client: DatasetClient,
                 latest_ohlc_chart_flow_callback: Callable,

                 limit=150,
                 is_eth=False,
                 data_format=ChartDataFormat.POLARS
                 ):
        self.full_symbol = full_symbol.upper()
        self.interval = interval
        self.api_client = api_client
        self.latest_ohlc_chart_flow_callback = latest_ohlc_chart_flow_callback
        self.limit = limit
        self.is_eth = is_eth
        self.data_format = data_format
        self.schema_asset, self.country_symbol = self.full_symbol.split(":", 1)
        self.df: pl.DataFrame = None

    def receive_subscribe_ohlc_data_1m(self, data: Dict):

        if self.df is None or not data:
            return None

        temp_df = OhlcAggregationMinute(self.df, data, limit=self.limit).aggregate()

        if temp_df is None:
            return None

        self.df = temp_df

        return_data = to_format_data(self.df, self.data_format)
        self.latest_ohlc_chart_flow_callback(return_data)

    def __string_to_polars(self, api_result: UnifiedResponse | ErrorResponse) -> pl.DataFrame | None:
        df = None

        if api_result.code != 200:
            logger.warning(api_result)
            return df

        if not api_result.result["count"]:
            return df

        csv_string = api_result.result["data"]

        schema_overrides = {
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Float64,
            "vwap": pl.Float64,
        }

        df = pl.read_csv(
            io.BytesIO(csv_string.encode('utf-8')),
            schema_overrides=schema_overrides
        ).with_columns([
            pl.col("datetime").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%z"),
            pl.col("close_datetime").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%z")
        ])
        return df

    def __fix_week_mon_data(self):
        if self.interval not in [IntervalName.MON, IntervalName.WEEK]:
            return

        if self.df is None or self.df.is_empty():
            # logger.warning("Cannot fix data: base DataFrame is missing.")
            return

        from_date = self.df.item(-1, "datetime")
        to_date = datetime.now(timezone.utc)

        daily_data_chunks = []
        try:
            for history_ohlcs in self.api_client.ohlc.ohlcs(
                    schema_asset=self.schema_asset,
                    country_symbol=self.country_symbol,
                    interval=IntervalName.DAY,
                    from_date=from_date,
                    to_date=to_date,
                    limit=50,
                    is_eth=self.is_eth,
                    format="csv"
            ):
                daily_chunk = self.__string_to_polars(history_ohlcs)
                if daily_chunk is not None and not daily_chunk.is_empty():
                    daily_data_chunks.append(daily_chunk)
                break

            if not daily_data_chunks:
                # logger.debug("No new daily data found to fix the recent bar.")
                return

            day_df = pl.concat(daily_data_chunks)
        except Exception as e:
            # logger.error(f"Failed to fetch daily data for fixing bars: {e}")
            return

        # 2
        agg_exprs = [
            pl.col("open").first(),
            pl.col("high").max(),
            pl.col("low").min(),
            pl.col("close").last(),
            pl.col("volume").sum(),
            pl.col("close_datetime").last(),
        ]

        # 3
        aggregated_df = None
        if self.interval == IntervalName.WEEK:
            offset = "0d"
            try:

                weekday_counts = self.df['datetime'].dt.weekday().value_counts()

                if not weekday_counts.is_empty():
                    dominant_start_day = weekday_counts.sort(
                        by=['count', 'datetime'], descending=[True, True]
                    ).item(0, 'datetime')

                    offset_val = -((8 - dominant_start_day) % 7)
                    offset = f"{offset_val}d"
                    #logger.debug(f"Auto-detected start day of the week: {dominant_start_day}, using offset: {offset}")

            except Exception as e:
                #logger.warning(f"Could not reliably determine the start day of the week. Falling back to the default (Monday). Error: {e}")
                pass

            aggregated_df = (
                day_df.sort("datetime")
                .group_by_dynamic(
                    "datetime", every="1w", closed="left", label="left", offset=offset
                )
                .agg(agg_exprs)
            )

        elif self.interval == IntervalName.MON:
            aggregated_df = (
                day_df.sort("datetime")
                .group_by_dynamic(
                    "datetime", every="1mo", closed="left", label="left"
                )
                .agg(agg_exprs)
            )

        if aggregated_df is not None and not aggregated_df.is_empty():

            aggregated_cols = set(aggregated_df.columns)

            last_row_template = self.df[-1, :]

            add_col_exprs = []

            for col_name in self.df.columns:
                if col_name not in aggregated_cols:
                    value = last_row_template.item(0, col_name)
                    add_col_exprs.append(pl.lit(value).alias(col_name))

            if add_col_exprs:
                aggregated_df = aggregated_df.with_columns(add_col_exprs)

            aggregated_df = aggregated_df.select(self.df.columns)

            self.df = (
                pl.concat([self.df[:-1], aggregated_df])
                .unique(subset=["datetime"], keep="last")
                .sort("datetime")
                .tail(self.limit)
            )
            # logger.debug(f"Successfully fixed and updated recent {self.interval} bar(s).")

    def run(self):
        ohlc_latest = self.api_client.ohlc.ohlcs_latest(
            schema_asset=self.schema_asset,
            country_symbol=self.country_symbol,
            interval=self.interval,
            limit=self.limit,
            is_eth=self.is_eth,
            format="csv",

        )
        return_data = None
        if (df := self.__string_to_polars(ohlc_latest)) is None:
            return return_data

        self.df = df
        self.__fix_week_mon_data()

        return_data = to_format_data(self.df, self.data_format)

        self.latest_ohlc_chart_flow_callback(return_data)
        return return_data
