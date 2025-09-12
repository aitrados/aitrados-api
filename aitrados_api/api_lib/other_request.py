from aitrados_api.api_lib.request_base_mixin import RequestBaseMixin
from aitrados_api.models.other_model import SERVER_ADDRESS_INFO_REQUEST_DATA


class OtherRequest(RequestBaseMixin):
    def server_address_info(self):
        params={}
        return self._common_requests.get_general_request(SERVER_ADDRESS_INFO_REQUEST_DATA,
                                                                params=params)