"""Client for the Investec API."""

import base64
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union, cast
from urllib.parse import urljoin

import requests

from investec_api.exceptions import (
    InvestecAPIError,
    InvestecAuthError,
    InvestecRateLimitError,
    InvestecRequestError,
)
from investec_api.models.account import Account, AccountBalance
from investec_api.models.beneficiary import Beneficiary, BeneficiaryCategory
from investec_api.models.document import Document
from investec_api.models.payment import (
    BeneficiaryPaymentItem,
    BeneficiaryPaymentRequest,
    PaymentResponse,
)
from investec_api.models.profile import AuthorisationSetup, Profile
from investec_api.models.transaction import PendingTransaction, Transaction
from investec_api.models.transfer import (
    TransferItem,
    TransferRequest,
    TransferResponse,
)


class InvestecClient:
    """Client for interacting with the Investec API."""

    PRODUCTION_URL = "https://openapi.investec.com"
    SANDBOX_URL = "https://openapisandbox.investec.com"
    TOKEN_URL_PATH = "/identity/v2/oauth2/token"
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_key: str,
        use_sandbox: bool = False,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Investec API client.

        Args:
            client_id: The OAuth client ID
            client_secret: The OAuth client secret
            api_key: The API key (x-api-key) value
            use_sandbox: Whether to use the sandbox environment (default: False)
            timeout: Timeout for API calls in seconds (default: 30)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.base_url = self.SANDBOX_URL if use_sandbox else self.PRODUCTION_URL
        self.timeout = timeout

        # Authentication state
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get the authentication headers for API requests."""
        if (
            not self._access_token
            or not self._token_expires_at
            or time.time() >= self._token_expires_at
        ):
            self._authenticate()

        return {
            "Authorization": f"Bearer {self._access_token}",
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }

    def _authenticate(self) -> None:
        """Authenticate with the Investec API and get an access token."""
        # Prepare basic auth (client_id:client_secret)
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "x-api-key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(
                urljoin(self.base_url, self.TOKEN_URL_PATH),
                headers=headers,
                data=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            auth_data = response.json()

            self._access_token = auth_data.get("access_token")
            expires_in = auth_data.get(
                "expires_in", 1799
            )  # Default to 30 minutes - 1 second
            self._token_expires_at = (
                time.time() + float(expires_in) - 60
            )  # Refresh 1 minute before expiry

            if not self._access_token:
                raise InvestecAuthError("No access token in response")

        except requests.exceptions.HTTPError as e:
            raise InvestecAuthError(f"Authentication failed: {str(e)}")
        except (requests.exceptions.RequestException, ValueError) as e:
            raise InvestecAuthError(f"Authentication request failed: {str(e)}")

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the Investec API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Form data
            json_data: JSON data for the request body

        Returns:
            API response as a dictionary
        """
        url = urljoin(self.base_url, path)
        headers = self._get_auth_headers()

        if json_data:
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout,
            )

            if response.status_code == 429:
                raise InvestecRateLimitError(
                    "Rate limit exceeded, retry after a delay",
                    response.status_code,
                    response.json() if response.text else None,
                )

            response.raise_for_status()

            # Some endpoints might return empty responses
            if not response.text:
                return {}

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                status_code = e.response.status_code
                error_data = None
                try:
                    if e.response.text:
                        error_data = e.response.json()
                except ValueError:
                    pass

                raise InvestecRequestError(
                    f"HTTP error occurred: {str(e)}",
                    status_code,
                    error_data,
                )
            raise InvestecAPIError(f"HTTP error occurred: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise InvestecAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise InvestecAPIError(f"Invalid JSON in response: {str(e)}")

    # Account Information Methods

    def get_accounts(self) -> List[Account]:
        """Get all accounts for the authenticated user.

        Returns:
            List of Account objects
        """
        response = self._request("GET", "/za/pb/v1/accounts")
        if "data" in response and "accounts" in response["data"]:
            return [
                Account.from_dict(account) for account in response["data"]["accounts"]
            ]
        return []

    def get_account_balance(self, account_id: str) -> AccountBalance:
        """Get the balance for a specific account.

        Args:
            account_id: The ID of the account

        Returns:
            AccountBalance object with balance information
        """
        response = self._request("GET", f"/za/pb/v1/accounts/{account_id}/balance")
        return AccountBalance.from_api_response(response)

    def get_account_transactions(
        self,
        account_id: str,
        from_date: Optional[Union[date, datetime, str]] = None,
        to_date: Optional[Union[date, datetime, str]] = None,
        transaction_type: Optional[str] = None,
        include_pending: bool = False,
    ) -> List[Transaction]:
        """Get transactions for a specific account.

        Args:
            account_id: The ID of the account
            from_date: Start date for transactions (default: 180 days ago)
            to_date: End date for transactions (default: today)
            transaction_type: Filter transactions by type
            include_pending: Include pending transactions

        Returns:
            List of Transaction objects
        """
        params: Dict[str, str] = {}

        # Format dates as ISO strings (YYYY-MM-DD)
        if from_date:
            if isinstance(from_date, (date, datetime)):
                params["fromDate"] = from_date.strftime("%Y-%m-%d")
            else:
                params["fromDate"] = str(from_date)

        if to_date:
            if isinstance(to_date, (date, datetime)):
                params["toDate"] = to_date.strftime("%Y-%m-%d")
            else:
                params["toDate"] = str(to_date)

        if transaction_type:
            params["transactionType"] = transaction_type

        if include_pending:
            params["includePending"] = "true"

        response = self._request(
            "GET", f"/za/pb/v1/accounts/{account_id}/transactions", params=params
        )

        if "data" in response and "transactions" in response["data"]:
            return [
                Transaction.from_dict(txn) for txn in response["data"]["transactions"]
            ]
        return []

    def get_account_pending_transactions(
        self, account_id: str
    ) -> List[PendingTransaction]:
        """Get pending transactions for a specific account.

        Args:
            account_id: The ID of the account

        Returns:
            List of PendingTransaction objects
        """
        response = self._request(
            "GET", f"/za/pb/v1/accounts/{account_id}/pending-transactions"
        )

        if "data" in response and "PendingTransaction" in response["data"]:
            return [
                PendingTransaction.from_dict(txn)
                for txn in response["data"]["PendingTransaction"]
            ]
        return []

    # Inter-account Transfer Methods

    def transfer_multiple(
        self,
        account_id: str,
        transfers: List[TransferItem],
        profile_id: Optional[str] = None,
    ) -> TransferResponse:
        """Transfer funds to one or multiple accounts.

        Args:
            account_id: The source account ID
            transfers: List of TransferItem objects
            profile_id: Optional profile ID

        Returns:
            TransferResponse with the result of the transfers
        """
        transfer_request = TransferRequest(
            transfer_list=transfers, profile_id=profile_id
        )

        response = self._request(
            "POST",
            f"/za/pb/v1/accounts/{account_id}/transfermultiple",
            json_data=transfer_request.to_dict(),
        )

        return TransferResponse.from_api_response(response)

    # Beneficiary Methods

    def get_beneficiaries(self) -> List[Beneficiary]:
        """Get all beneficiaries for the authenticated user.

        Returns:
            List of Beneficiary objects
        """
        response = self._request("GET", "/za/pb/v1/accounts/beneficiaries")
        # API returns an array directly in data
        if "data" in response and isinstance(response["data"], list):
            return [
                Beneficiary.from_dict(beneficiary) for beneficiary in response["data"]
            ]
        return []

    def get_beneficiary_categories(self) -> BeneficiaryCategory:
        """Get beneficiary categories.

        Returns:
            BeneficiaryCategory object
        """
        response = self._request("GET", "/za/pb/v1/accounts/beneficiarycategories")
        return BeneficiaryCategory.from_api_response(response)

    def pay_beneficiaries(
        self, account_id: str, payments: List[BeneficiaryPaymentItem]
    ) -> PaymentResponse:
        """Pay one or multiple beneficiaries.

        Args:
            account_id: The source account ID
            payments: List of BeneficiaryPaymentItem objects

        Returns:
            PaymentResponse with the result of the payments
        """
        payment_request = BeneficiaryPaymentRequest(payment_list=payments)

        response = self._request(
            "POST",
            f"/za/pb/v1/accounts/{account_id}/paymultiple",
            json_data=payment_request.to_dict(),
        )

        return PaymentResponse.from_api_response(response)

    # Profile Methods

    def get_profiles(self) -> List[Profile]:
        """Get all profiles for the authenticated user.

        Returns:
            List of Profile objects
        """
        response = self._request("GET", "/za/pb/v1/profiles")
        if "data" in response and isinstance(response["data"], list):
            return [Profile.from_dict(profile) for profile in response["data"]]
        return []

    def get_profile_accounts(self, profile_id: str) -> List[Account]:
        """Get all accounts for a specific profile.

        Args:
            profile_id: The ID of the profile

        Returns:
            List of Account objects
        """
        response = self._request("GET", f"/za/pb/v1/profiles/{profile_id}/accounts")
        if "data" in response and isinstance(response["data"], list):
            return [Account.from_dict(account) for account in response["data"]]
        return []

    def get_authorisation_setup(
        self, profile_id: str, account_id: str
    ) -> AuthorisationSetup:
        """Get authorisation setup details for a specific account.

        Args:
            profile_id: The ID of the profile
            account_id: The ID of the account

        Returns:
            AuthorisationSetup object
        """
        response = self._request(
            "GET",
            f"/za/pb/v1/profiles/{profile_id}/accounts/{account_id}/authorisationsetupdetails",
        )
        return AuthorisationSetup.from_api_response(response)

    def get_profile_beneficiaries(
        self, profile_id: str, account_id: str
    ) -> List[Beneficiary]:
        """Get all beneficiaries for a specific profile and account.

        Args:
            profile_id: The ID of the profile
            account_id: The ID of the account

        Returns:
            List of Beneficiary objects
        """
        response = self._request(
            "GET",
            f"/za/pb/v1/profiles/{profile_id}/accounts/{account_id}/beneficiaries",
        )
        if "data" in response and isinstance(response["data"], list):
            return [
                Beneficiary.from_dict(beneficiary) for beneficiary in response["data"]
            ]
        return []

    # Document Methods

    def get_documents(
        self,
        account_id: str,
        from_date: Union[date, datetime, str],
        to_date: Union[date, datetime, str],
    ) -> List[Document]:
        """Get all documents for a specific account within a date range.

        Args:
            account_id: The ID of the account
            from_date: Start date for documents
            to_date: End date for documents

        Returns:
            List of Document objects
        """
        params: Dict[str, str] = {}

        # Format dates as ISO strings (YYYY-MM-DD)
        if isinstance(from_date, (date, datetime)):
            params["fromDate"] = from_date.strftime("%Y-%m-%d")
        else:
            params["fromDate"] = str(from_date)

        if isinstance(to_date, (date, datetime)):
            params["toDate"] = to_date.strftime("%Y-%m-%d")
        else:
            params["toDate"] = str(to_date)

        response = self._request(
            "GET", f"/za/pb/v1/accounts/{account_id}/documents", params=params
        )
        if "data" in response and isinstance(response["data"], list):
            return [Document.from_dict(document) for document in response["data"]]
        return []

    def get_document(
        self,
        account_id: str,
        document_type: str,
        document_date: Union[date, datetime, str],
    ) -> bytes:
        """Get a specific document.

        Args:
            account_id: The ID of the account
            document_type: The type of document
            document_date: The date of the document

        Returns:
            Raw document data as bytes
        """
        # Format date as ISO string (YYYY-MM-DD)
        if isinstance(document_date, (date, datetime)):
            date_str = document_date.strftime("%Y-%m-%d")
        else:
            date_str = str(document_date)

        url = urljoin(
            self.base_url,
            f"/za/pb/v1/accounts/{account_id}/document/{document_type}/{date_str}",
        )
        headers = self._get_auth_headers()

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                status_code = e.response.status_code
                error_data = None
                try:
                    if e.response.text:
                        error_data = e.response.json()
                except ValueError:
                    pass

                raise InvestecRequestError(
                    f"HTTP error occurred: {str(e)}",
                    status_code,
                    error_data,
                )
            raise InvestecAPIError(f"HTTP error occurred: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise InvestecAPIError(f"Request failed: {str(e)}")
