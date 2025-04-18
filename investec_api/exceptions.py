"""Exceptions for the Investec API client."""

from typing import Any, Dict, Optional


class InvestecAPIError(Exception):
    """Base exception for all Investec API errors."""

    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.response = response


class InvestecAuthError(InvestecAPIError):
    """Exception raised when authentication fails."""

    pass


class InvestecRequestError(InvestecAPIError):
    """Exception raised when a request to the API fails."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, response)
        self.status_code = status_code


class InvestecRateLimitError(InvestecRequestError):
    """Exception raised when rate limits are hit."""

    pass
