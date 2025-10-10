from typing import List
import io
import pandas as pd
import polars as pl

from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse



class AnyListDataToFormatData:
    def __init__(self, any_list_data: str | list | pl.DataFrame | pd.DataFrame,
                 rename_column_name_mapping: dict = None,
                 filter_column_names: List[str] = None,
                 limit: int = None):
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

    def _apply_processing(self):
        if self._pandas_df is None:
            return

        if self.rename_column_name_mapping:
            self._pandas_df = self._pandas_df.rename(columns=self.rename_column_name_mapping)

        if self.filter_column_names:
            available_columns = [col for col in self.filter_column_names if col in self._pandas_df.columns]
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
                available_columns = [col for col in self.filter_column_names if col in self._polars_df.columns]
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

    def get_csv(self) -> None | str:
        # If the data is empty, return None directly
        if self._is_empty:
            return None

        if self._is_polars_native and self._polars_df is not None:
            try:
                return self._polars_df.write_csv()
            except Exception:
                return None

        if self._pandas_df is None or self._pandas_df.empty:
            return None

        try:
            return self._pandas_df.to_csv(index=False)
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















class ApiListResultToFormatData:
    def __init__(self,api_result:UnifiedResponse|ErrorResponse,rename_column_name_mapping:dict=None,filter_column_names:List[str]=None,limit=None):
        self.api_result=api_result
        self.list_data=None
        self.is_empty_data=False
        self.rename_column_name_mapping=rename_column_name_mapping
        self.filter_column_names=filter_column_names
        self.limit=limit

        self.any_list_data_to_format_data:AnyListDataToFormatData=None

        self.__init_data()

    def __init_data(self):
        if not isinstance(self.api_result,UnifiedResponse):
            return

        if self.api_result.code != 200:
            return
        result=self.api_result.result
        if "count" not in  result or  "data" not in result:
            return

        if not result["count"]:
            self.is_empty_data=True
            return


        self.list_data = self.api_result.result["data"]
        self.any_list_data_to_format_data=AnyListDataToFormatData(self.list_data, self.rename_column_name_mapping,self.filter_column_names,self.limit )


    def __is_direct_result(self):
        if self.is_empty_data:
            return True,None
        if not self.list_data:
            return True,self.api_result

        return False,None



    def get_csv(self)->None | str|ErrorResponse:
        is_direct,result= self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_csv()


    def get_pandas(self)->None|pd.DataFrame|ErrorResponse:
        is_direct,result= self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_pandas()
    def get_polars(self)->None|pl.DataFrame|ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_polars()
    def get_list(self) -> None | list|ErrorResponse:
        is_direct, result = self.__is_direct_result()
        if is_direct:
            return result
        return self.any_list_data_to_format_data.get_list()
