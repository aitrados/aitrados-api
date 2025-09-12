
from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.ohlc_model import OHLC_HISTORY_LIST_REQUEST_DATA, OHLC_LATEST_LIST_REQUEST_DATA


class OhlcRequest(RequestBaseMixin):

    def ohlcs(self, schema_asset, country_symbol, interval, from_date, to_date, format="json", limit=150):
        """
        Function to request OHLC data from the API.

        :param schema_asset: Schema asset (e.g., crypto, stock)
        :param country_symbol: Stock symbol (ticker)
        :param interval: Time interval (e.g., 1min, 5min, 15min, 30min, 1hour, 4hour)
        :param from_date: Start date in YYYY-MM-DD format
        :param to_date: End date in YYYY-MM-DD format
        :param format: Data format (default is "json")
        :param limit: Data count limit (default is 150, max is 1000)
        :param secret_key: API secret key
        :return: Response from the API
        """

        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
            "interval": interval,
            "from_date": from_date,
            "to_date": to_date,
            "format": format,
            "limit": limit,
        }

        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(OHLC_HISTORY_LIST_REQUEST_DATA,
                                                                              params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def ohlcs_latest(self, schema_asset, country_symbol, interval, format="json", limit=150, **kwargs):

        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
            "interval": interval,
            "format": format,
            "limit": limit,
        }

        return self._common_requests.get_general_request(OHLC_LATEST_LIST_REQUEST_DATA, params=params)
