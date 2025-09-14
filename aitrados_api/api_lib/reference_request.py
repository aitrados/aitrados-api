from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.reference_model import REFERENCE_REQUEST_DATA, OPTION_SEARCH_REQUEST_DATA, \
    OPTIONS_EXPIRATION_DATE_LIST_REQUEST_DATA, STOCK_CORPORATE_ACTION_LIST_REQUEST_DATA


class ReferenceRequest(RequestBaseMixin):

    def reference(self, schema_asset: str, country_symbol: str):
        """
        Function to request reference data from the API.

        :param schema_asset: Schema asset (e.g., crypto, stock)
        :param country_symbol: country symbol (e.g., US:TSLA)
        :return: Response from the API
        """
        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,

        }

        return self._common_requests.get_general_request(REFERENCE_REQUEST_DATA, params=params)

    def search_option(self,
                      schema_asset: str,
                      country_symbol: str,
                      option_type: str,
                      moneyness: str,
                      ref_asset_price: float = None,
                      strike_price: float = None,
                      expiration_date: str = None,
                      limit: int = 100,
                      sort_by: str = None):
        """
        Function to search options based on various parameters.

        :param schema_asset: Schema asset (e.g., stock)
        :param country_symbol: Country symbol (e.g., US:SPY)
        :param option_type: Type of option (e.g., call, put)
        :param moneyness: Moneyness of the option (e.g., in_the_money, out_of_the_money)
        :param ref_asset_price: Reference asset price for moneyness calculation
        :param strike_price: Specific strike price to filter options
        :param expiration_date: Expiration date of the options
        :param limit: Number of results to return
        :param sort_by: Sorting criteria for the results
        :return: Response from the API
        """
        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
            "option_type": option_type,
            "moneyness": moneyness,
            "ref_asset_price": ref_asset_price,
            "strike_price": strike_price,
            "expiration_date": expiration_date,
            "limit": limit,
            "sort_by": sort_by
        }
        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(OPTION_SEARCH_REQUEST_DATA, params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def options_expiration_date_list(self, schema_asset: str, country_symbol: str):
        """
        Function to get a list of option expiration dates.

        :param schema_asset: Schema asset (e.g., stock)
        :param country_symbol: Country symbol (e.g., US:SPY)
        :param limit: Number of results to return
        :return: Response from the API
        """
        params = {
            "schema_asset": schema_asset,
            "country_symbol": country_symbol,
        }

        return self._common_requests.get_general_request(OPTIONS_EXPIRATION_DATE_LIST_REQUEST_DATA, params=params)
    def stock_corporate_action_list(self,country_symbol: str,from_date,action_type=None,to_date=None,format="json",limit=100,next_page_key=None):

        params = {
            "country_symbol": country_symbol,
            "action_type": action_type,
            "from_date": from_date,
            "to_date": to_date,
            "format": format,
            "limit": limit,
            "next_page_key": next_page_key


        }
        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(STOCK_CORPORATE_ACTION_LIST_REQUEST_DATA, params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

