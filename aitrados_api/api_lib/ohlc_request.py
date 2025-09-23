
from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.common_lib.contant import ApiDataFormat
from aitrados_api.models.ohlc_model import OHLC_HISTORY_LIST_REQUEST_DATA, OHLC_LATEST_LIST_REQUEST_DATA


class OhlcRequest(RequestBaseMixin):

    def ohlcs(self, schema_asset,
              country_symbol:str,
              interval:str,
              from_date:any,
              to_date:any,
              format:str=ApiDataFormat.CSV,
              limit=150,
              sort=None,
              is_eth=False #US stock extended hour
              ):


        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
            "interval": interval,
            "from_date": from_date,
            "to_date": to_date,
            "format": format,
            "limit": limit,
            "sort": sort,
            "is_eth":is_eth
        }

        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(OHLC_HISTORY_LIST_REQUEST_DATA,
                                                                              params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def ohlcs_latest(self, schema_asset:str,
                     country_symbol:str,
                     interval:str,
                     format:str=ApiDataFormat.CSV,
                     limit=150,
                     is_eth=False
                     , **kwargs):

        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
            "interval": interval,
            "format": format,
            "limit": limit,
            "is_eth": is_eth
        }

        return self._common_requests.get_general_request(OHLC_LATEST_LIST_REQUEST_DATA, params=params)
