import types
import warnings
from pydantic import ValidationError as PydanticValidationError

from aitrados_api.api_lib.common_request import CommonRequests
from aitrados_api.api_lib.economic_request import EconomicRequest
from aitrados_api.api_lib.holiday_request import HolidayRequest
from aitrados_api.api_lib.news_request import NewsRequest
from aitrados_api.api_lib.ohlc_request import OhlcRequest
from aitrados_api.api_lib.other_request import OtherRequest
from aitrados_api.api_lib.reference_request import ReferenceRequest
from aitrados_api.common_lib.contant import ApiEndpoint
from aitrados_api.common_lib.exceptions import ConfigError
from aitrados_api.common_lib.http_api.base import BaseClient
from aitrados_api.common_lib.http_api.config import ClientConfig
from aitrados_api.common_lib.common import logger


class DatasetClient(BaseClient):
    """Main client for Dataset Data API"""

    def __init__(
        self,
        secret_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        base_url: str = f"{ApiEndpoint.DEFAULT}/api",
        config: ClientConfig | None = None,

    ):
        self._initialized: bool = False



        common_requests = CommonRequests(self)

        self.ohlc=OhlcRequest(self,common_requests)
        self.reference=ReferenceRequest(self,common_requests)

        self.economic = EconomicRequest(self,common_requests)
        self.holiday=HolidayRequest(self,common_requests)
        self.news = NewsRequest(self,common_requests)
        self.other=OtherRequest(self,common_requests)





        if not secret_key and (config is None or not config.secret_key):
            raise ConfigError("Invalid client configuration: API key is required")

        try:
            if config is not None:
                self._config = config
            else:


                try:
                    self._config = ClientConfig(
                        secret_key=secret_key or "",  # Handle None case
                        timeout=timeout,
                        max_retries=max_retries,
                        base_url=base_url,

                    )
                except PydanticValidationError as e:
                    raise ConfigError("Invalid client configuration") from e



            super().__init__(self._config)
            self._initialized = True

        except Exception as e:


            raise

    @classmethod
    def from_env(cls, debug: bool = False) -> "DatasetClient":
        """
        Create client instance from environment variables

        Args:
            debug: Enable debug logging if True
        """
        config = ClientConfig.from_env()

        return cls(config=config)

    def __enter__(self) -> "DatasetClient":
        """Context manager enter"""
        if not self._initialized:
            raise RuntimeError("Client not properly initialized")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """
        Context manager exit

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.close()


    def close(self) -> None:
        """Clean up resources"""
        try:
            if hasattr(self, "client") and self.client is not None:
                self.client.close()
            if hasattr(self, "_initialized") and self._initialized:
                logger.info("Dataset Data client closed")


        except Exception as e:
            logger.error(f"Error during cleanup: {e!s}")

    def __del__(self) -> None:
        """Destructor that ensures resources are cleaned up"""
        try:
            if hasattr(self, "_initialized") and self._initialized:
                self.close()
        except (Exception, BaseException) as e:
            # Suppress any errors during cleanup
            warnings.warn(
                f"Error during DatasetDataClient cleanup: {e!s}",
                ResourceWarning,
                stacklevel=2,
            )






