from loguru import logger

import pandas as pd
import polars as pl

from aitrados_api.common_lib.contant import ChartDataFormat


def get_full_symbol(data: dict | list[dict] | pd.DataFrame | pl.DataFrame)->str:
    if isinstance(data, pd.DataFrame):
        if not all(col in data.columns for col in ["asset_schema", "country_iso_code", "symbol"]):
            raise ValueError("pandas DataFrame missing required columns: 'asset_schema', 'country_iso_code', 'symbol'")
        # For pandas, .iloc[-1] returns a Series, and .to_dict() works as expected.
        data = data.iloc[-1].to_dict()

    elif isinstance(data, pl.DataFrame):
        if data.is_empty():
            raise ValueError("Input polars DataFrame is empty.")
        if not all(col in data.columns for col in ["asset_schema", "country_iso_code", "symbol"]):
            raise ValueError("polars DataFrame missing required columns: 'asset_schema', 'country_iso_code', 'symbol'")
        # Corrected line: Use .row(-1, named=True) to get a dict of scalar values for the last row.
        # The original `data[-1].to_dict()` was incorrect.
        data = data.row(-1, named=True)

    elif isinstance(data, list):
        if not data:
            raise ValueError("Input list is empty.")
        data = data[-1]

    # After potential conversion, we expect `data` to be a dictionary.
    if not isinstance(data, dict):
        raise TypeError(f"Unsupported data type or failed conversion: {type(data)}")

    asset_schema = data.get("asset_schema")
    country_iso_code = data.get("country_iso_code")
    symbol = data.get("symbol")
    if not all([asset_schema, country_iso_code, symbol]):
        raise ValueError("Input data missing required fields: 'asset_schema', 'country_iso_code', 'symbol'")

    full_symbol = f"{asset_schema}:{country_iso_code}:{symbol}".upper()
    return full_symbol


def to_format_data(df: pl.DataFrame, data_format: str,is_copy=True) -> str | list | dict | pd.DataFrame | pl.DataFrame:
    # 优化：以 Polars DataFrame 为基础进行格式转换
    if data_format == ChartDataFormat.CSV:
        return df.write_csv()
    elif data_format == ChartDataFormat.DICT:
        return df.with_columns(
            pl.col(pl.Datetime).dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        ).to_dicts()
    elif data_format == ChartDataFormat.PANDAS:
        return df.to_pandas()
    elif data_format == ChartDataFormat.POLARS:
        return df.clone() if is_copy else df
    else:
        raise ValueError(f"Unsupported data format: {data_format}")