import traceback

import json
from typing import List, Dict, Any
import io
import pandas as pd
import polars as pl

from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse, get_standard_response


class AnyToFormat:
    CSV = "csv"
    PANDAS = "pandas"
    POLARS = "polars"
    LIST = "list"

    @classmethod
    def get_array(cls):
        return [cls.CSV, cls.PANDAS, cls.POLARS, cls.LIST]

    @classmethod
    def get_serialized_array(cls):
        return [cls.CSV, cls.LIST]


class AnyListDataToFormatData:
    def __init__(self, any_list_data: str | list | pl.DataFrame | pd.DataFrame,
                 rename_column_name_mapping: dict = None,
                 filter_column_names: List[str] = None,
                 limit: int = None):
        """

        :param any_list_data:
        :param rename_column_name_mapping:  eg. rename interval to timeframe:{"interval": "timeframe"}
        :param filter_column_names: like [ "timeframe","open", "high", "low", "close", "volume"]
        :param limit:
        """

        self.any_list_data = any_list_data
        self.rename_column_name_mapping = rename_column_name_mapping or {}
        self.filter_column_names = filter_column_names
        self.limit = limit
        self._pandas_df = None
        self._polars_df = None
        self._processed_data = None
        self._is_polars_native = False
        self._is_empty = False

        self._init_data()

    def _init_data(self):
        try:
            if isinstance(self.any_list_data, str):
                self._pandas_df = pd.read_csv(io.StringIO(self.any_list_data))
                self._apply_processing()
            elif isinstance(self.any_list_data, list):
                if not self.any_list_data:
                    self._pandas_df = pd.DataFrame()
                else:
                    self._pandas_df = pd.DataFrame(self.any_list_data)
                self._apply_processing()
            elif isinstance(self.any_list_data, pl.DataFrame):
                self._polars_df = self.any_list_data.clone()
                self._is_polars_native = True
                self._apply_processing_polars()
            elif isinstance(self.any_list_data, pd.DataFrame):
                self._pandas_df = self.any_list_data.copy()
                self._apply_processing()
            else:
                raise ValueError(f"Unsupported data type: {type(self.any_list_data)}")

            self._check_empty()

        except Exception as e:
            raise ValueError(f"Failed to initialize data: {str(e)}")

    def _check_empty(self):

        if self._is_polars_native:
            if self._polars_df is None or self._polars_df.height == 0:
                self._is_empty = True
        else:
            if self._pandas_df is None or len(self._pandas_df) == 0:
                self._is_empty = True

    def _get_processed_filter_columns(self, df_columns):
        if not self.filter_column_names:
            return []

        post_rename_filter_names = [self.rename_column_name_mapping.get(col, col) for col in self.filter_column_names]

        unique_cols = list(dict.fromkeys(post_rename_filter_names))

        available_columns = [col for col in unique_cols if col in df_columns]

        return available_columns

    def _apply_processing(self):
        if self._pandas_df is None:
            return
        # rename_column_name_mapping:  like {"interval": "timeframe"}
        # filter_column_names: like [ "interval","open", "high", "low", "close", "volume"]

        if self.rename_column_name_mapping:
            self._pandas_df = self._pandas_df.rename(columns=self.rename_column_name_mapping)

        if self.filter_column_names:
            available_columns = self._get_processed_filter_columns(self._pandas_df.columns)
            if available_columns:
                self._pandas_df = self._pandas_df[available_columns]

        if self.limit and len(self._pandas_df) > self.limit:
            self._pandas_df = self._pandas_df.tail(self.limit)

    def _apply_processing_polars(self):
        if self._polars_df is None:
            return

        try:
            if self.rename_column_name_mapping:
                self._polars_df = self._polars_df.rename(self.rename_column_name_mapping)

            if self.filter_column_names:
                available_columns = self._get_processed_filter_columns(self._polars_df.columns)
                if available_columns:
                    self._polars_df = self._polars_df.select(available_columns)

            if self.limit and self._polars_df.height > self.limit:
                self._polars_df = self._polars_df.tail(self.limit)

        except Exception as e:
            self._polars_df = None
            raise ValueError(f"Failed to process polars DataFrame: {str(e)}")

    def _ensure_polars(self):
        if self._polars_df is None and self._pandas_df is not None:
            try:
                self._polars_df = pl.from_pandas(self._pandas_df)
            except Exception as e:
                return None
        return self._polars_df

    def _ensure_pandas(self):
        if self._pandas_df is None and self._polars_df is not None:
            try:
                self._pandas_df = self._polars_df.to_pandas()
                self._apply_processing()
            except Exception as e:
                return None
        return self._pandas_df

    @classmethod
    def _get_formatted_float_column_df(self, df: pd.DataFrame | pl.DataFrame):

        if isinstance(df, pl.DataFrame):

            float_columns = [
                col for col in df.columns
                if df[col].dtype in [pl.Float32, pl.Float64]
            ]

            if not float_columns:
                return df

            formatted_df = df.with_columns([
                pl.when(pl.col(col).abs() < 10)
                .then(pl.col(col).round(4))
                .otherwise(pl.col(col).round(2))
                .alias(col)
                for col in float_columns
            ])
            return formatted_df

        elif isinstance(df, pd.DataFrame):

            formatted_df = df.copy()

            float_columns = formatted_df.select_dtypes(include=['float32', 'float64']).columns

            for col in float_columns:
                mask = formatted_df[col].abs() < 10
                formatted_df.loc[mask, col] = formatted_df.loc[mask, col].round(4)
                formatted_df.loc[~mask, col] = formatted_df.loc[~mask, col].round(2)

            return formatted_df

        else:
            raise ValueError(f"Unsupported DataFrame type: {type(df)}")

    def get_csv(self) -> None | str:
        # If the data is empty, return None directly
        if self._is_empty:
            return None

        if self._is_polars_native and self._polars_df is not None:
            try:
                temp_df = self._get_formatted_float_column_df(self._polars_df)
                return temp_df.write_csv()
            except Exception:

                return None

        if self._pandas_df is None or self._pandas_df.empty:
            return None

        try:
            temp_df = self._get_formatted_float_column_df(self._pandas_df)
            return temp_df.to_csv(index=False)
        except Exception:
            return None

    def get_pandas(self) -> None | pd.DataFrame:
        # If data is empty, return None instead of an empty DataFrame
        if self._is_empty:
            return None

        if self._is_polars_native:
            pandas_df = self._ensure_pandas()
            if pandas_df is not None:
                return pandas_df.copy()
            return None

        if self._pandas_df is None:
            return None
        return self._pandas_df.copy()

    def get_polars(self) -> None | pl.DataFrame:
        # If the data is empty, return None directly
        if self._is_empty:
            return None

        if self._is_polars_native and self._polars_df is not None:
            return self._polars_df.clone()

        polars_df = self._ensure_polars()
        if polars_df is None:
            return None
        return polars_df.clone()

    def get_list(self) -> None | list:
        # If the data is empty, return None directly
        if self._is_empty:
            return None

        if self._is_polars_native and self._polars_df is not None:
            try:
                return self._polars_df.to_dicts()
            except Exception:
                return None

        if self._pandas_df is None or self._pandas_df.empty:
            return None

        try:
            return self._pandas_df.to_dict('records')
        except Exception:
            return None

    def get_data(self, to_format: str = "polars"):
        if to_format == AnyToFormat.CSV:
            return self.get_csv()
        elif to_format == AnyToFormat.PANDAS:
            return self.get_pandas()
        elif to_format == AnyToFormat.POLARS:
            return self.get_polars()
        elif to_format == AnyToFormat.LIST:
            return self.get_list()
        else:
            return self.get_csv()


class ApiListResultToFormatData:
    def __init__(self, api_result: UnifiedResponse | ErrorResponse, rename_column_name_mapping: dict = None,
                 filter_column_names: List[str] = None, limit=None):
        self.api_result = api_result
        self.list_data = None
        self.is_empty_data = False
        self.rename_column_name_mapping = rename_column_name_mapping
        self.filter_column_names = filter_column_names
        self.limit = limit

        self.any_list_data_to_format_data: AnyListDataToFormatData = None

        self.__init_data()

    def __init_data(self):
        if not isinstance(self.api_result, UnifiedResponse):
            return

        if self.api_result.code != 200:
            return
        result = self.api_result.result
        if "count" not in result or "data" not in result:
            return

        if not result["count"]:
            self.is_empty_data = True
            return

        self.list_data = self.api_result.result["data"]
        self.any_list_data_to_format_data = AnyListDataToFormatData(self.list_data, self.rename_column_name_mapping,
                                                                    self.filter_column_names, self.limit)

    def __is_direct_result(self):
        if self.is_empty_data:
            return True, None
        if not self.list_data:
            return True, self.api_result

        return False, None

    def get_csv(self) -> None | str | ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_csv()

    def get_pandas(self) -> None | pd.DataFrame | ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_pandas()

    def get_polars(self) -> None | pl.DataFrame | ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_polars()

    def get_list(self) -> None | list | ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_list()


class ApiListResultToFormatData2(ApiListResultToFormatData):
    def __init__(self, data: dict, rename_column_name_mapping: dict = None,
                 filter_column_names: List[str] = None, limit=None):

        if data["code"] == 200:
            api_result = UnifiedResponse(**data)
        else:
            api_result = ErrorResponse(**data)
        super().__init__(api_result=api_result,
                         rename_column_name_mapping=rename_column_name_mapping,
                         filter_column_names=filter_column_names,
                         limit=limit
                         )


def any_data_to_format_data(data: any,
                            rename_column_name_mapping: dict = None,
                            filter_column_names: List[str] = None,
                            limit: int = None,
                            to_format: str = "polars"):
    if to_format not in AnyToFormat.get_array():
        to_format = "polars"

    def abc_to():
        converter = AnyListDataToFormatData(
            data,
            rename_column_name_mapping=rename_column_name_mapping,
            filter_column_names=filter_column_names,
            limit=limit
        )
        return converter.get_data(to_format)

    if isinstance(data, list | pl.DataFrame | pd.DataFrame):
        return abc_to()

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return abc_to()
    if "code" in data and "status" in data:
        response = get_standard_response(data)
        if response.code != 200:
            raise ValueError(f"{response}")
        if isinstance(response.result, dict) and "data" in response.result:
            data = response.result['data']
        else:
            data = response.result
    return abc_to()


def deserialize_multi_symbol_multi_timeframe_data(
        data: dict | str,
        rename_column_name_mapping: dict = None,
        filter_column_names: List[str] = None,
        limit: int = None,
        to_format: str = "polars"
) -> Dict[str, List[Any]]:
    """
    Unserialize multi-symbol multi-timeframe data from ZeroMQ message.

    This function deserializes data received from ZeroMQ publisher, converting CSV strings
    or other data formats back to the specified target format (polars, pandas, csv, or list).

    Args:
        msg: The message data, can be dict or JSON string containing symbol data
        rename_column_name_mapping: Optional dictionary to rename columns during processing
        filter_column_names: Optional list of column names to filter/select
        limit: Optional limit on number of rows to return
        to_format: Target format for conversion ("polars", "pandas", "csv", "list")

    Returns:
        Dictionary mapping full_symbol to list of converted data in specified format

    Raises:
        ValueError: If to_format is not supported or JSON parsing fails

    Example:
        >>> data = unserialize_multi_symbol_multi_timeframe_data(
        ...     data='{"NASDAQ:AAPL": ["csv_data1", "csv_data2"]}',
        ...     to_format="polars"
        ... )
        >>> # Returns: {"NASDAQ:AAPL": [polars_df1, polars_df2]}
    """
    # Validate target format
    if to_format not in AnyToFormat.get_array():
        to_format = "polars"

    new_push_data = {}

    # Parse JSON string if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON message: {e}")

    if "code" in data and "status" in data:
        response = get_standard_response(data)
        if response.code != 200:
            raise ValueError(f"Failed to parse JSON message: {response}")
        if isinstance(response.result, dict) and "data" in response.result:
            data = response.result['data']
        else:
            data = response.result

    # Process each symbol's data
    for full_symbol, data_list in data.items():
        converted_data_list = []

        for data in data_list:
            try:
                # Create converter instance with processing parameters
                converter = AnyListDataToFormatData(
                    data,
                    rename_column_name_mapping=rename_column_name_mapping,
                    filter_column_names=filter_column_names,
                    limit=limit
                )
                converted_data = converter.get_data(to_format)

                # Only append non-None results
                if converted_data is not None:
                    converted_data_list.append(converted_data)

            except Exception as e:
                # Log error but continue processing other data items
                print(f"Warning: Failed to convert data for {full_symbol}: {e}")
                continue

        # Only include symbols that have successfully converted data
        if converted_data_list:
            new_push_data[full_symbol] = converted_data_list

    return new_push_data
