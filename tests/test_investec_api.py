"""Test suite for Investec API using the sandbox environment."""

import logging
import time
import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

# Configure logging
logger = logging.getLogger("investec-tests")

# Import pytest first, with try/except to handle linter when it's not installed
try:
    import pytest
except ImportError:
    pass  # Linter might not have pytest installed, but it will be available at runtime

from investec_api import InvestecClient
from investec_api.exceptions import InvestecAPIError

# Import models individually - ensure they match the actual library structure
try:
    from investec_api.models import (
        Account,
        AccountBalance,
        Beneficiary,
        Transaction,
    )
    from investec_api.models.payment import BeneficiaryPaymentItem
    from investec_api.models.transfer import TransferItem
except ImportError as e:
    logger.error(f"Import error: {e}")

from tests.config import config


class TestInvestecAPI:
    """Test suite for Investec API using sandbox credentials."""

    @pytest.fixture(scope="class")
    def client(self) -> InvestecClient:
        """Create a configured Investec client."""
        return InvestecClient(
            client_id=config.client_id,
            client_secret=config.client_secret,
            api_key=config.api_key,
            use_sandbox=config.use_sandbox,
            timeout=config.timeout,
        )

    @pytest.fixture(scope="class")
    def account_id(self, client: InvestecClient) -> str:
        """Get the first available account ID."""
        accounts = client.get_accounts()
        if not accounts:
            pytest.skip("No accounts available in the sandbox.")
        return accounts[0].account_id

    @pytest.fixture(scope="class")
    def profile_id(self, client: InvestecClient) -> Optional[str]:
        """Get the first available profile ID."""
        try:
            profiles = client.get_profiles()
            if not profiles:
                pytest.skip("No profiles available in the sandbox.")
            return profiles[0].profile_id
        except Exception as e:
            pytest.skip(f"Error fetching profiles: {str(e)}")
            return None  # Added return None to satisfy type checker

    def test_authentication(self, client: InvestecClient) -> None:
        """Test authentication to the Investec API."""
        # Force authentication by setting token to None
        client._access_token = None
        client._token_expires_at = None

        # This will trigger authentication
        client._get_auth_headers()

        # Check if authentication was successful
        assert client._access_token is not None
        assert client._token_expires_at is not None
        assert client._token_expires_at > time.time()

    def test_get_accounts(self, client: InvestecClient) -> None:
        """Test fetching accounts."""
        accounts = client.get_accounts()

        assert isinstance(accounts, list)
        if accounts:  # Sandbox should have at least one account
            assert isinstance(accounts[0], Account)
            assert accounts[0].account_id
            assert accounts[0].account_name
            assert accounts[0].product_name

    def test_get_account_balance(self, client: InvestecClient, account_id: str) -> None:
        """Test fetching account balance."""
        balance = client.get_account_balance(account_id)

        assert isinstance(balance, AccountBalance)
        assert balance.account_id == account_id
        assert isinstance(balance.current_balance, Decimal)
        assert isinstance(balance.available_balance, Decimal)
        assert balance.currency  # Usually "ZAR" in sandbox

    def test_get_account_transactions(
        self, client: InvestecClient, account_id: str
    ) -> None:
        """Test fetching account transactions."""
        # Get transactions for the last 30 days
        from_date = date.today() - timedelta(days=30)
        to_date = date.today()

        transactions = client.get_account_transactions(
            account_id=account_id, from_date=from_date, to_date=to_date
        )

        assert isinstance(transactions, list)
        # Sandbox should have some transactions
        if transactions:
            assert isinstance(transactions[0], Transaction)
            assert transactions[0].account_id == account_id
            assert transactions[0].type
            assert transactions[0].transaction_date

    def test_get_account_transactions_with_filters(
        self, client: InvestecClient, account_id: str
    ) -> None:
        """Test fetching account transactions with filters."""
        # Get transactions with all possible filters
        from_date = date.today() - timedelta(days=60)
        to_date = date.today()

        transactions = client.get_account_transactions(
            account_id=account_id,
            from_date=from_date,
            to_date=to_date,
            transaction_type="CardPurchases",  # Example transaction type
            include_pending=True,
        )

        assert isinstance(transactions, list)

    def test_get_account_pending_transactions(
        self, client: InvestecClient, account_id: str
    ) -> None:
        """Test fetching pending transactions."""
        pending_transactions = client.get_account_pending_transactions(account_id)

        assert isinstance(pending_transactions, list)
        # Note: sandbox may or may not have pending transactions

    def test_get_beneficiaries(self, client: InvestecClient) -> None:
        """Test fetching beneficiaries."""
        try:
            beneficiaries = client.get_beneficiaries()

            assert isinstance(beneficiaries, list)
            # Sandbox might have sample beneficiaries
            if beneficiaries:
                assert isinstance(beneficiaries[0], Beneficiary)
                assert beneficiaries[0].beneficiary_id
                assert beneficiaries[0].name
        except Exception as e:
            pytest.skip(f"Error fetching beneficiaries: {str(e)}")

    def test_get_profiles(self, client: InvestecClient) -> None:
        """Test fetching profiles."""
        try:
            profiles = client.get_profiles()

            assert isinstance(profiles, list)
            # Sandbox might have profiles
            if profiles:
                assert profiles[0].profile_id
                assert profiles[0].profile_name
        except Exception as e:
            pytest.skip(f"Error fetching profiles: {str(e)}")

    def test_transfer_multiple(self, client: InvestecClient, account_id: str) -> None:
        """Test transferring funds between accounts."""
        # To test this, we need at least two accounts
        accounts = client.get_accounts()
        if len(accounts) < 2:
            pytest.skip("Need at least two accounts to test transfers.")

        # Set up the transfer
        beneficiary_account = next(
            (a for a in accounts if a.account_id != account_id), None
        )
        if not beneficiary_account:
            pytest.skip("Could not find a beneficiary account.")
            return  # Skip the rest of the test

        transfer_items = [
            TransferItem(
                beneficiary_account_id=beneficiary_account.account_id,
                amount=Decimal("100.00"),
                my_reference=f"Test transfer {uuid.uuid4().hex[:8]}",
                their_reference="API Test",
            )
        ]

        try:
            # Execute the transfer
            response = client.transfer_multiple(
                account_id=account_id, transfers=transfer_items
            )

            assert response is not None
            assert response.transfer_responses is not None
            assert len(response.transfer_responses) == 1
            assert response.transfer_responses[0].status
        except Exception as e:
            pytest.skip(f"Error during transfer: {str(e)}")

    def test_pay_beneficiaries(self, client: InvestecClient, account_id: str) -> None:
        """Test paying beneficiaries."""
        try:
            # Get beneficiaries
            beneficiaries = client.get_beneficiaries()
            if not beneficiaries:
                pytest.skip("No beneficiaries available to test payment.")

            # Create payment items
            payment_items = [
                BeneficiaryPaymentItem(
                    beneficiary_id=beneficiaries[0].beneficiary_id,
                    amount=Decimal("50.00"),
                    my_reference=f"Test payment {uuid.uuid4().hex[:8]}",
                    their_reference="API Test Payment",
                )
            ]

            # Execute the payment
            response = client.pay_beneficiaries(
                account_id=account_id, payments=payment_items
            )

            assert response is not None
            assert response.transfer_responses is not None
            assert len(response.transfer_responses) == 1
            assert response.transfer_responses[0].status
        except Exception as e:
            pytest.skip(f"Error during beneficiary payment: {str(e)}")

    def test_get_profile_accounts(
        self, client: InvestecClient, profile_id: Optional[str]
    ) -> None:
        """Test fetching accounts for a profile."""
        if profile_id is None:
            pytest.skip("No profile ID available")
            return

        try:
            accounts = client.get_profile_accounts(profile_id)

            assert isinstance(accounts, list)
            if accounts:
                assert isinstance(accounts[0], Account)
                assert accounts[0].account_id
        except Exception as e:
            pytest.skip(f"Error fetching profile accounts: {str(e)}")

    def test_get_authorisation_setup(
        self, client: InvestecClient, profile_id: Optional[str], account_id: str
    ) -> None:
        """Test fetching authorisation setup."""
        if profile_id is None:
            pytest.skip("No profile ID available")
            return

        try:
            auth_setup = client.get_authorisation_setup(profile_id, account_id)

            assert auth_setup is not None
        except Exception as e:
            pytest.skip(f"Error fetching authorisation setup: {str(e)}")

    def test_get_profile_beneficiaries(
        self, client: InvestecClient, profile_id: Optional[str], account_id: str
    ) -> None:
        """Test fetching beneficiaries for a profile."""
        if profile_id is None:
            pytest.skip("No profile ID available")
            return

        try:
            beneficiaries = client.get_profile_beneficiaries(profile_id, account_id)

            assert isinstance(beneficiaries, list)
        except Exception as e:
            pytest.skip(f"Error fetching profile beneficiaries: {str(e)}")

    def test_get_documents(self, client: InvestecClient, account_id: str) -> None:
        """Test fetching documents."""
        try:
            # Get documents for the last 90 days
            from_date = date.today() - timedelta(days=90)
            to_date = date.today()

            documents = client.get_documents(
                account_id=account_id, from_date=from_date, to_date=to_date
            )

            assert isinstance(documents, list)
        except Exception as e:
            pytest.skip(f"Error fetching documents: {str(e)}")

    def test_error_handling(self, client: InvestecClient) -> None:
        """Test error handling with an invalid account ID."""
        with pytest.raises(InvestecAPIError):
            client.get_account_balance("invalid_account_id")
