"""
Investec API MCP Configuration

This module provides configuration for the Investec API MCP server using Pydantic for type safety.
"""

import logging
import os

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv(find_dotenv(usecwd=True))

# Configure logging
logger = logging.getLogger("investec-config")


class InvestecConfig(BaseSettings):
    """Pydantic model for Investec API configuration."""

    # API credentials
    client_id: str = Field(..., description="Investec API client ID")
    client_secret: str = Field(..., description="Investec API client secret")
    api_key: str = Field(..., description="Investec API key")

    # Environment configuration
    use_sandbox: bool = Field(
        False, description="Whether to use the sandbox environment"
    )
    timeout: int = Field(30, description="Timeout for API calls in seconds")

    # Base URLs
    production_url: str = Field(
        "https://openapi.investec.com", description="Production API URL"
    )
    sandbox_url: str = Field(
        "https://openapisandbox.investec.com", description="Sandbox API URL"
    )

    @property
    def base_url(self) -> str:
        """Return the appropriate base URL based on the environment."""
        return self.sandbox_url if self.use_sandbox else self.production_url

    @property
    def token_url(self) -> str:
        """Return the full OAuth token URL."""
        return f"{self.base_url}/identity/v2/oauth2/token"

    def model_post_init(self, __context) -> None:
        """Log configuration status after initialization."""
        logger.debug(
            "Configuration: client_id=%s, client_secret=%s, api_key=%s, use_sandbox=%s, timeout=%s",
            f"{self.client_id[:4]}..." if self.client_id else "Not set",
            "***" if self.client_secret else "Not set",
            "***" if self.api_key else "Not set",
            self.use_sandbox,
            self.timeout,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


def load_config(test_mode: bool = False) -> InvestecConfig:
    """
    Load configuration with support for both prefixed and non-prefixed variables.

    This function supports both INVESTEC_* prefixed variables and non-prefixed
    versions for backwards compatibility.

    Args:
        test_mode: If True, uses the sandbox environment by default and
                  provides test default values if credentials aren't set.
    """
    # Test default values (used only in test_mode if no real values are provided)
    test_defaults = {
        "client_id": "yAxzQRFX97vOcyQAwluEU6H6ePxMA5eY",
        "client_secret": "4dY0PjEYqoBrZ99r",
        "api_key": "eUF4elFSRlg5N3ZPY3lRQXdsdUVVNkg2ZVB4TUE1ZVk6YVc1MlpYTjBaV010ZW1FdGNHSXRZV05qYjNWdWRITXRjMkZ1WkdKdmVBPT0=",
        "use_sandbox": True,
    }

    # First check for prefixed variables
    try:
        config_args = {
            "client_id": os.environ.get("INVESTEC_CLIENT_ID", ""),
            "client_secret": os.environ.get("INVESTEC_CLIENT_SECRET", ""),
            "api_key": os.environ.get("INVESTEC_API_KEY", ""),
            "use_sandbox": test_mode
            or os.environ.get("INVESTEC_USE_SANDBOX", "").lower() == "true",
            "timeout": int(os.environ.get("INVESTEC_TIMEOUT", "30")),
            "production_url": os.environ.get(
                "INVESTEC_PRODUCTION_URL", "https://openapi.investec.com"
            ),
            "sandbox_url": os.environ.get(
                "INVESTEC_SANDBOX_URL", "https://openapisandbox.investec.com"
            ),
        }

        # If any required field is missing, we'll fall through to non-prefixed variables
        if (
            not config_args["client_id"]
            or not config_args["client_secret"]
            or not config_args["api_key"]
        ):
            raise ValueError("Missing required credentials with INVESTEC_ prefix")

        return InvestecConfig(**config_args)
    except Exception:
        # Try non-prefixed variables
        config_args = {
            "client_id": os.environ.get("CLIENT_ID", ""),
            "client_secret": os.environ.get("CLIENT_SECRET", ""),
            "api_key": os.environ.get("API_KEY", ""),
            "use_sandbox": test_mode
            or os.environ.get("USE_SANDBOX", "").lower() == "true",
            "timeout": int(os.environ.get("TIMEOUT", "30")),
            "production_url": os.environ.get(
                "PRODUCTION_URL", "https://openapi.investec.com"
            ),
            "sandbox_url": os.environ.get(
                "SANDBOX_URL", "https://openapisandbox.investec.com"
            ),
        }

        # In test mode, apply test defaults if credentials are missing
        if test_mode:
            if not config_args["client_id"]:
                config_args["client_id"] = test_defaults["client_id"]
            if not config_args["client_secret"]:
                config_args["client_secret"] = test_defaults["client_secret"]
            if not config_args["api_key"]:
                config_args["api_key"] = test_defaults["api_key"]
            if not os.environ.get("USE_SANDBOX"):
                config_args["use_sandbox"] = test_defaults["use_sandbox"]

        return InvestecConfig(**config_args)


# Create a global instance to be imported for regular use
config = load_config()
