import asyncio
import os
import pathlib
from typing import List

from dotenv import load_dotenv
from loguru import logger

from aitrados_api.common_lib.tools.toml_manager import TomlManager

logger.remove()
logger.add(
    sink=lambda message: print(message, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True
)



import pandas as pd
import polars as pl

from aitrados_api.common_lib.contant import ChartDataFormat, IntervalName, SchemaAsset


def run_asynchronous_function(func):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():

        loop.create_task(func)
    else:
        asyncio.run(func)
def get_real_interval(interval:str):
    array=IntervalName.get_array()

    if not interval:
        raise ValueError(f"Invalid interval format. Expected '{array}'.")
    interval=interval.upper()
    if interval not in array:
        raise ValueError(f"Invalid interval format. Expected '{array}'.")
    return interval
def get_real_intervals(intervals:List[str]):
    new_intervals=[]
    array = IntervalName.get_array()
    if not intervals:
        raise ValueError(f"Invalid intervals format. Expected value in  '{array}'.")

    intervals=set(intervals)

    for  interval in intervals:
        new_intervals.append(get_real_interval(interval))
    return new_intervals

def split_full_symbol(full_symbol:str):
    if not isinstance(full_symbol, str) or full_symbol.count(':') < 2:
        raise ValueError(f"Invalid full_symbol ({full_symbol}) format. Expected 'ASSET_NAME:COUNTRY_ISO_CODE:SYMBOL'.")
    full_symbol=full_symbol.upper()
    asset_name, country_symbol = full_symbol.split(':', 1)
    if asset_name.lower() not in SchemaAsset.get_array():
        raise ValueError(f"Invalid asset name: '{asset_name}' of '{full_symbol}'. Expected one of {SchemaAsset.get_array()}.")
    return asset_name, country_symbol
def get_fixed_full_symbol(full_symbol:str):
    asset_name, country_symbol=split_full_symbol(full_symbol)
    standard_full_symbol_key = f"{asset_name}:{country_symbol}"
    return standard_full_symbol_key



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

def is_debug():
    string=os.getenv("DEBUG","false").lower()
    if string in ["1","true"]:
        return True
    return False
def get_env_bool_value(env_key):
    string=os.getenv(env_key,"false").lower()
    if string in ["1","true"]:
        return True
    return False

def get_env_value(env_key,default_value=None):
    value=os.getenv(env_key, default_value)
    try:
        value=int(value)
    except:
        try:
            value = float(value)
        except:
            pass
    return value
def load_env_file(file=None,override=False):

    env_path=None
    if file:
        env_path = pathlib.Path(file)
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file not found: {env_path}")
    else:
        possible_paths = [
            pathlib.Path.cwd() / '.env',
            pathlib.Path.cwd() / '../.env',
            pathlib.Path.cwd() / '../../.env',
            pathlib.Path.cwd() / '../../../.env',
        ]
        for path in possible_paths:
            if path.exists():
                env_path = path
                break

        if not env_path:
            raise FileNotFoundError(f"Environment file not found in common paths: {possible_paths}\nPlease Input file parameter")

    load_dotenv(env_path,override=override)
def load_global_configs(env_file =None, toml_file=None):
    if not os.getenv('AITRADOS_SECRET_KEY'):
        load_env_file(file=env_file,override=True)
    if not TomlManager.c:
        TomlManager.load_toml_file(file=toml_file)