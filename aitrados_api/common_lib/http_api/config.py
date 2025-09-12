import os
from urllib.parse import urlparse

from aitrados_api.common_lib.common import logger


from pydantic import BaseModel, ConfigDict, Field, field_validator

from aitrados_api.common_lib.contant import ApiEndpoint
from aitrados_api.common_lib.exceptions import ConfigError






class RateLimitConfig(BaseModel):
    """Rate limit configuration"""

    daily_limit: int = Field(default=250, gt=0, description="Maximum daily API calls")
    requests_per_second: int = Field(
        default=5,
        gt=0,
        description="Maximum requests per second",
    )
    requests_per_minute: int = Field(
        default=300, gt=0, description="Maximum requests per minute"
    )

    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        """Create rate limit config from environment variables"""

        def safe_int(env_var: str, default: str) -> int:
            """Safely convert environment variable to int, falling back to default"""
            try:
                return int(os.getenv(env_var, default))
            except (ValueError, TypeError):
                return int(default)

        return cls(
            daily_limit=safe_int("DATASET_DAILY_LIMIT", "10000"),
            requests_per_second=safe_int("DATASET_REQUESTS_PER_SECOND", "5"),
            requests_per_minute=safe_int("DATASET_REQUESTS_PER_MINUTE", "300"),
        )


class ClientConfig(BaseModel):
    """Base client configuration for Dataset Data API"""

    # Configure model
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    secret_key: str = Field(
        description="AITRADOS secret key. Can be set via Dataset_API_KEY environment variable",
        repr=False,  # Exclude API key from repr
    )
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")
    max_retries: int = Field(
        default=3, ge=0, description="Maximum number of request retries"
    )
    max_rate_limit_retries: int = Field(
        default=3, ge=0, description="Maximum number of rate limit retries"
    )
    base_url: str = Field(
        default=f"{ApiEndpoint.DEFAULT}/api", description="Base API endpoint URL"
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limit configuration",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate API key is not empty"""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        if v=="YOUR_SECRET_KEY":
            logger.error("Please set your actual API key instead of the placeholder YOUR_SECRET_KEY")
            raise ValueError("Please set your actual API key instead of the placeholder YOUR_SECRET_KEY")

        return v.strip()

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format"""
        if not v or not v.strip():
            raise ValueError("Base URL cannot be empty")

        v = v.strip()
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {v}")
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"URL scheme must be http or https: {v}")
        except Exception as e:
            raise ValueError(f"Invalid URL: {v}") from e

        v+="/api"
        return v

    def __str__(self) -> str:
        data = self.model_dump()
        if data.get("secret_key"):

            secret_key = data["secret_key"]

            if len(secret_key) > 4:
                data["secret_key"] = f"{secret_key[:4]}***"
            else:
                data["secret_key"] = "***"

        # Create a string representation from the masked data
        fields = []
        for key, value in data.items():
            if key == "secret_key":
                fields.append(f"secret_key='{value}'")
            elif isinstance(value, str):
                fields.append(f"{key}='{value}'")
            else:
                fields.append(f"{key}={value}")

        return " ".join(fields)

    def __repr__(self) -> str:
        """Representation with masked API key"""
        return f"{self.__class__.__name__}({self.__str__()})"

    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables"""
        secret_key = os.getenv("AITRADOS_SECRET_KEY")
        if not secret_key:
            raise ConfigError(
                "API key must be provided either "
                "explicitly or via DATASET_API_KEY environment variable"
            )

        def safe_int(env_var: str, default: str) -> int:
            """Safely convert environment variable to int, falling back to default"""
            try:
                return int(os.getenv(env_var, default))
            except (ValueError, TypeError):
                return int(default)

        config_dict = {
            "secret_key": secret_key,
            "timeout": safe_int("DATASET_TIMEOUT", "30"),
            "max_retries": safe_int("DATASET_MAX_RETRIES", "3"),
            "base_url": os.getenv(
                "DATASET_BASE_URL", f"{ApiEndpoint.DEFAULT}/api"
            ),
            "rate_limit": RateLimitConfig.from_env(),
        }

        return cls(**config_dict)
