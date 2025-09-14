
from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.news_model import NEWS_LIST_REQUEST_DATA, NEWS_LATEST_REQUEST_DATA


class NewsRequest(RequestBaseMixin):

    def news_list(self,
                  from_date: str,
                  to_date: str,
                  full_symbol: str | None = None,
                  sort: str | None = "asc",
                  limit: int | None = 100,
                  format: str | None = "json",

                  next_page_key: str | None = None, ):

        params = {
            "full_symbol": full_symbol,
            "from_date": from_date,
            "to_date": to_date,
            "sort": sort,
            "limit": limit,
            "format": format,
            "next_page_key": next_page_key,
        }
        while True:

            redata, next_page_key = self._common_requests.common_iterate_list(NEWS_LIST_REQUEST_DATA, params=params)
            yield redata
            if next_page_key:
                params["next_page_key"] = next_page_key
            else:
                break

    def news_latest(self,
                    full_symbol: str = None,
                    sort: str = None,
                    limit: int = 5,
                    ):

        params = {
            "full_symbol": full_symbol,
            "sort": sort,
            "limit": limit,

        }

        return self._common_requests.get_general_request(NEWS_LATEST_REQUEST_DATA,
                                                         params=params)
