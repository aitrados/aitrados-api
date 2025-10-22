from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.economic_model import EVENT_LIST_REQUEST_DATA, EVENT_REQUEST_DATA, EVENT_CODES_REQUEST_DATA, \
    LATEST_EVENT_LIST_REQUEST_DATA


class EconomicRequest(RequestBaseMixin):

    def event_list(self,
                   country_iso_code: str | None = None,
                   event_code: str | None = None,
                   impact: str | None = None,#"impact (low,medium,high)
                   source_id: str | None = None,
                   from_date: str | None = None,
                   to_date: str | None = None,
                   sort: str=None,
                   limit: int | None = 100,
                   format: str | None = "json",
                   next_page_key:str=None,

                   ):

        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact":impact,
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

    async def a_event_list(self,
                           country_iso_code: str | None = None,
                           event_code: str | None = None,
                           impact: str | None = None,  # "impact (low,medium,high)
                           source_id: str | None = None,
                           from_date: str | None = None,
                           to_date: str | None = None,
                           sort: str = None,
                           limit: int | None = 100,
                           format: str | None = "json",
                           next_page_key: str = None,

                           ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact": impact,
            "source_id": source_id,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,
            "limit": limit,
            "format": format,
            "next_page_key": next_page_key,
        }
        while True:
            redata, next_page_key = await self._common_requests.a_common_iterate_list(EVENT_LIST_REQUEST_DATA,
                                                                                      params=params)
            yield redata

            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def event(self,
              country_iso_code: str | None = None,
              event_code: str | None = None,
              impact: str | None = None,  # "impact (low,medium,high)
              source_id: str | None = None,
              from_date: str | None = None,
              to_date: str | None = None,
              sort: str =None,
              ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact": impact,
            "source_id": source_id,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,

        }

        return self._common_requests.get_general_request(EVENT_REQUEST_DATA,
                                                         params=params)

    async def a_event(self,
                      country_iso_code: str | None = None,
                      event_code: str | None = None,
                      impact: str | None = None,  # "impact (low,medium,high)
                      source_id: str | None = None,
                      from_date: str | None = None,
                      to_date: str | None = None,
                      sort: str = None,
                      ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact": impact,
            "source_id": source_id,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,
        }
        return await self._common_requests.a_get_general_request(EVENT_REQUEST_DATA,
                                                                 params=params)

    def event_codes(self, country_iso_code: str = "US"):
        params = {
            "country_iso_code": country_iso_code,

        }
        return self._common_requests.get_general_request(EVENT_CODES_REQUEST_DATA,
                                                         params=params)

    async def a_event_codes(self, country_iso_code: str = "US"):
        params = {
            "country_iso_code": country_iso_code,
        }
        return await self._common_requests.a_get_general_request(EVENT_CODES_REQUEST_DATA,
                                                                 params=params)

    def latest_events(self,
                      country_iso_code: str | None = None,
                      event_code: str | None = None,
                      impact: str | None = None,  # "impact (low,medium,high)
                      date_type: str="upcoming",  #(upcoming or historical and all)
                      limit: int | None = 5,
                      format: str | None = "json",
                      sort: str = None,
                      ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact": impact,
            "date_type": date_type,
            "limit": limit,
            "format":format,


            "sort": sort,
        }
        return  self._common_requests.get_general_request(LATEST_EVENT_LIST_REQUEST_DATA,
                                                                 params=params)
    async def a_latest_events(self,
                      country_iso_code: str | None = None,
                      event_code: str | None = None,
                      impact: str | None = None,  #"impact (low,medium,high)
                      date_type: str="upcoming",#(upcoming or historical and all)
                      limit: int | None = 5,
                      format: str | None = "json",
                      sort: str = None,
                      ):
        params = {
            "country_iso_code": country_iso_code,
            "event_code": event_code,
            "impact": impact,
            "date_type": date_type,
            "limit": limit,
            "format":format,


            "sort": sort,
        }
        return await self._common_requests.a_get_general_request(LATEST_EVENT_LIST_REQUEST_DATA,
                                                                 params=params)
