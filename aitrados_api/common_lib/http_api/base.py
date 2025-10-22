import logging
import math
import time
from typing import Any, TypeVar
import warnings
import asyncio
import httpx

from pydantic import BaseModel
from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log, after_log, retry

from aitrados_api.common_lib.http_api.config import ClientConfig


from aitrados_api.common_lib.exceptions import (
    AuthenticationError,
    DatasetError,
    RateLimitError,
    ValidationError,
)




from aitrados_api.common_lib.http_api.rate_limit import DatasetRateLimiter, QuotaConfig
from aitrados_api.common_lib.response_format import UnifiedResponse, ErrorResponse
from aitrados_api.models.base_model import Endpoint,APIVersion


T = TypeVar("T", bound=BaseModel)


from aitrados_api.common_lib.common import logger, run_asynchronous_function


class BaseClient:
    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the BaseClient with the provided configuration.
        """
        self.config = config

        self.max_rate_limit_retries = getattr(config, "max_rate_limit_retries", 3)
        self._rate_limit_retry_count = 0
        self._setup_http_client()
        self._setup_async_http_client()
        self._rate_limiter = DatasetRateLimiter(
            QuotaConfig(
                daily_limit=self.config.rate_limit.daily_limit,
                requests_per_second=self.config.rate_limit.requests_per_second,
                requests_per_minute=self.config.rate_limit.requests_per_minute,
            )
        )


    def _setup_http_client(self) -> None:
        """
        Setup HTTP client with default configuration.
        """
        self.client = httpx.Client(
            timeout=self.config.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Dataset-Python-Client/1.0",
                "Accept": "application/json",
            },
        )
    def _setup_async_http_client(self) -> None:
        """
        Setup Async HTTP client with default configuration.
        """
        self.async_client = httpx.AsyncClient(
            timeout=self.config.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Dataset-Python-Client/1.0",
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        """
        Clean up resources (close the httpx client).
        """
        if hasattr(self, "client") and self.client is not None:
            self.client.close()
        run_asynchronous_function(self.aclose())

    async def aclose(self) -> None:
        """Asynchronously closes the HTTP clients."""
        if hasattr(self, "async_client") and self.async_client and not self.async_client.is_closed:
            await self.async_client.aclose()
    def _handle_rate_limit(self, wait_time: float) -> None:
        """
        Handle rate limiting by waiting or raising an exception based on retry count.
        """
        self._rate_limit_retry_count += 1

        if self._rate_limit_retry_count > self.max_rate_limit_retries:
            self._rate_limit_retry_count = 0  # Reset for next request
            raise RateLimitError(
                f"Rate limit exceeded after "
                f"{self.max_rate_limit_retries} retries. "
                f"Please wait {wait_time:.1f} seconds",
                retry_after=wait_time,
            )



        time.sleep(wait_time)



    def sleeping_task(self,) -> None:

        allow,limit_type=self._rate_limiter.should_allow_request()
        while not allow:
            wait_time = self._rate_limiter.get_wait_time()
            wait_time=math.ceil(wait_time)
            if wait_time==0:
                return

            #if self.config.debug:
            logger.warning(f"AITRADOS API -> Rate limit({limit_type}) exceeded. Please wait {wait_time} seconds")

            time.sleep(math.ceil(wait_time))
    async def a_sleeping_task(self) -> None:

        allow, limit_type = self._rate_limiter.should_allow_request()
        while not allow:
            wait_time = self._rate_limiter.get_wait_time()
            wait_time = math.ceil(wait_time)
            if wait_time == 0:
                return

            logger.warning(f"AITRADOS API -> Rate limit({limit_type}) exceeded. Please wait {wait_time} seconds")
            await asyncio.sleep(math.ceil(wait_time))


    @retry(
        stop=stop_after_attempt(100000),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        ),
        #before_sleep=before_sleep_log(logger, logging.WARNING),
        #after=after_log(logger, logging.INFO),
    )
    def request(self, endpoint: Endpoint[T],fail_action="quit", **kwargs: Any) -> UnifiedResponse|ErrorResponse:
        self.sleeping_task()
        self._rate_limit_retry_count = 0  # Reset counter at start of new request

        try:
            self._rate_limiter.record_request()

            # Validate and process parameters
            validated_params = endpoint.validate_params(kwargs)

            base_url=self.config.base_url

            # Build URL
            url = endpoint.build_url(base_url, validated_params)

            # Extract query parameters and add API key
            query_params = endpoint.get_query_params(validated_params)
            query_params["secret_key"] = self.config.secret_key



            response = self.client.request(
                endpoint.method.value, url, params=query_params
            )


            if self.config.debug:
                logger.debug(f"AITRADOS API -> Request:  {response.url} - Status: {response.status_code}")


            # Handle 429 responses from the API
            if response.status_code == 429:
                self._rate_limiter.handle_response(response.status_code, response.text)
                wait_time = self._rate_limiter.get_wait_time()
                raise RateLimitError(
                    f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                    retry_after=wait_time,
                )

            data = self.handle_response(response)
            return data



        except Exception as e:

            raise

    def handle_response(self, response: httpx.Response) -> UnifiedResponse|ErrorResponse:

        try:
            # 这将为 4xx 和 5xx 状态码触发异常
            response.raise_for_status()
            data = response.json()

            if data["code"]!=200:
                data = ErrorResponse(**data)
            else:
                data=UnifiedResponse(**data)


            # 现在 mypy 知道这是 dict[str, Any] | list[Any]
        except httpx.HTTPStatusError as e:
            # 检查状态码以决定如何操作
            status_code = e.response.status_code

            # 对于服务端错误 (5xx)，我们希望重试，所以重新抛出原始异常
            if status_code >= 500 and status_code!=422:
                raise e

            # 对于客户端错误 (4xx)，我们不重试，而是返回一个 ErrorResponse
            try:
                data = e.response.json()
                if "status" not in data:
                    raise e
                data = ErrorResponse(**data)
                #data = ErrorResponse( status=data.get("status", "Unknown error"), message=data.get("message", "Unknown error"),detail=data.get("detail", None), reference=data.get("reference", None))
            except :
                data = ErrorResponse(status="request_error", message="Unknown error")
        except:
            data=ErrorResponse(status="request_error", message="Unknown error")
        return data



    @retry(
        stop=stop_after_attempt(100000),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)
        ),
        # before_sleep=before_sleep_log(logger, logging.WARNING),
        # after=after_log(logger, logging.INFO),
    )
    async def a_request(self, endpoint: Endpoint[T], fail_action="quit",
                        **kwargs: Any) -> UnifiedResponse | ErrorResponse:
        """
        Make async request with rate limiting and retry logic.

        Args:
            endpoint: The Endpoint object describing the request (method, path, etc.).
            fail_action: Action to take on failure (currently not used).
            **kwargs: Arbitrary keyword arguments passed as request parameters.

        Returns:
            A UnifiedResponse or ErrorResponse object.
        """
        await self.a_sleeping_task()

        self._rate_limit_retry_count = 0  # Reset counter at start of new request

        try:
            self._rate_limiter.record_request()

            # Validate and process parameters
            validated_params = endpoint.validate_params(kwargs)

            base_url = self.config.base_url

            # Build URL
            url = endpoint.build_url(base_url, validated_params)

            # Extract query parameters and add API key
            query_params = endpoint.get_query_params(validated_params)
            query_params["secret_key"] = self.config.secret_key

            response = await self.async_client.request(
                endpoint.method.value, url, params=query_params
            )

            if self.config.debug:
                logger.debug(f"AITRADOS API -> Request:  {response.url} - Status: {response.status_code}")

            # Handle 429 responses from the API
            if response.status_code == 429:
                self._rate_limiter.handle_response(response.status_code, response.text)
                wait_time = self._rate_limiter.get_wait_time()
                raise RateLimitError(
                    f"Rate limit exceeded. Please wait {wait_time:.1f} seconds",
                    retry_after=wait_time,
                )

            data = self.handle_response(response)
            return data

        except Exception as e:
            raise


class EndpointGroup:
    """Abstract base class for endpoint groups"""

    def __init__(self, client: BaseClient) -> None:
        self._client = client

    @property
    def client(self) -> BaseClient:
        """Get the client instance."""
        return self._client
