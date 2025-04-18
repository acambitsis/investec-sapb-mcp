"""Account and balance models for the Investec API."""

from decimal import Decimal

from investec_api.models.base import BaseModel


class Account(BaseModel):
    """Investec bank account information."""

    account_id: str
    account_number: str
    account_name: str
    reference_name: str
    product_name: str
    kyc_compliant: bool
    profile_id: str
    profile_name: str

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """Create an Account instance from API response data."""
        return cls(
            account_id=data.get("accountId", ""),
            account_number=data.get("accountNumber", ""),
            account_name=data.get("accountName", ""),
            reference_name=data.get("referenceName", ""),
            product_name=data.get("productName", ""),
            kyc_compliant=data.get("kycCompliant", False),
            profile_id=data.get("profileId", ""),
            profile_name=data.get("profileName", ""),
        )


class AccountBalance(BaseModel):
    """Investec bank account balance information."""

    account_id: str
    current_balance: Decimal
    available_balance: Decimal
    budget_balance: Decimal
    straight_balance: Decimal
    cash_balance: Decimal
    currency: str

    @classmethod
    def from_dict(cls, data: dict) -> "AccountBalance":
        """Create an AccountBalance instance from API response data."""
        return cls(
            account_id=data.get("accountId", ""),
            current_balance=Decimal(str(data.get("currentBalance", 0))),
            available_balance=Decimal(str(data.get("availableBalance", 0))),
            budget_balance=Decimal(str(data.get("budgetBalance", 0))),
            straight_balance=Decimal(str(data.get("straightBalance", 0))),
            cash_balance=Decimal(str(data.get("cashBalance", 0))),
            currency=data.get("currency", "ZAR"),
        )
