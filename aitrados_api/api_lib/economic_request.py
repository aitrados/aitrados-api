from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.economic_model import EVENT_LIST_REQUEST_DATA, EVENT_REQUEST_DATA, EVENT_CODES_REQUEST_DATA


class EconomicRequest(RequestBaseMixin):

    def event_list(self,
                   country_iso_code: str | None = None,
                   event_code: str | None = None,
                   source_id: str | None = None,
                   from_date: str | None = None,
                   to_date: str | None = None,
                   sort: str=None,
                   limit: int | None = 100,
                   format: str | None = "json",
                   next_page_key:str=None,
                   ):
        """
        Function to request a list of economic calendar events.
        :param country_iso_code: Country ISO code (e.g., US, CN).
        :param event_code: Event code.
        :param source_id: Source ID.
        :param from_date: Start date for filtering events.
        :param to_date: End date for filtering events.
        :param sort: Sort direction ('asc' or 'desc').
        :param limit: Number of results to return.
        :param format: Data format ('json' or 'csv').
        :param debug: Enable debug mode (0 or 1).
        :return: Response from the API.
        """
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "source_id": source_id,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,
            "limit": limit,
            "format": format,
            "next_page_key": next_page_key,

        }

        while True:
            redata, next_page_key = self._common_requests.common_iterate_list(EVENT_LIST_REQUEST_DATA, params=params)

            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def event(self,
              country_iso_code: str | None = None,
              event_code: str | None = None,
              source_id: str | None = None,
              from_date: str | None = None,
              to_date: str | None = None,
              sort: str =None,
              ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "source_id": source_id,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,

        }

        return self._common_requests.get_general_request(EVENT_REQUEST_DATA,
                                                         params=params)

    def event_codes(self, country_iso_code: str = "US"):
        params = {
            "country_iso_code": country_iso_code,

        }

        return self._common_requests.get_general_request(EVENT_CODES_REQUEST_DATA,
                                                         params=params)
