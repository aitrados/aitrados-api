from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.holiday_model import HOLIDAY_LIST_REQUEST_DATA, HOLIDAY_CODES_REQUEST_DATA


class HolidayRequest(RequestBaseMixin):

    def holiday_list(self,
                     full_symbol: str,
                     from_date: str,
                     holiday_code: str | None = None,

                     to_date: str | None = None,
                     sort: str | None = "asc",
                     limit: int | None = 100,
                     format: str | None = "json",
                     next_page_key: str | None = None, ):

        params = {
            "full_symbol": full_symbol,
            "holiday_code": holiday_code,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,
            "limit": limit,
            "format": format,
            "next_page_key": next_page_key,
        }
        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(HOLIDAY_LIST_REQUEST_DATA, params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def holiday_codes(self, country_iso_code: str = "US"):

        params = {
            "country_iso_code": country_iso_code,

        }

        return self._common_requests.get_general_request(HOLIDAY_CODES_REQUEST_DATA,
                                                         params=params)
