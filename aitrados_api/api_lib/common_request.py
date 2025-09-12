from aitrados_api.common_lib.http_api.base import EndpointGroup
from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse
from aitrados_api.models.base_model import Endpoint


class CommonRequests(EndpointGroup):
    def get_general_request(self, endpoint: Endpoint, params: dict = None, fail_action="quit") -> any:
        if not params:
            params = {}

        return self.client.request(endpoint, fail_action=fail_action, **params)

    def common_iterate_list(self, request_data_key, params) -> tuple[UnifiedResponse | ErrorResponse, str | None]:
        redata = self.get_general_request(request_data_key, params=params)
        next_page_key = None
        if isinstance(redata, UnifiedResponse):
            result = redata.result
            next_page_key = result.get("next_page_key", None)
        return redata, next_page_key
