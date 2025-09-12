from aitrados_api.api_lib.common_request import CommonRequests


class RequestBaseMixin:
    def __init__(self, client,common_requests):
        """
        Initialize the OhlcRequest class with a client.

        :param client: An instance of DatasetClient or similar that handles API requests.
        """
        self._client = client
        self._common_requests:CommonRequests = common_requests
