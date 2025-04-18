"""Transaction models for the Investec API."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from investec_api.models.base import BaseModel


class TransactionType(str, Enum):
    """Type of transaction (credit or debit)."""

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionStatus(str, Enum):
    """Status of transaction (posted or pending)."""

    POSTED = "POSTED"
    PENDING = "PENDING"


class Transaction(BaseModel):
    """Transaction information for an Investec bank account."""

    account_id: str
    type: TransactionType
    transaction_type: Optional[str] = None
    status: TransactionStatus
    description: str
    card_number: Optional[str] = None
    posted_order: Optional[int] = None
    posting_date: Optional[datetime] = None
    value_date: Optional[datetime] = None
    action_date: Optional[datetime] = None
    transaction_date: Optional[datetime] = None
    amount: Decimal
    running_balance: Optional[Decimal] = None
    uuid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create a Transaction instance from API response data."""
        # Convert string dates to datetime objects if present
        posting_date = None
        if "postingDate" in data and data["postingDate"]:
            try:
                posting_date = datetime.fromisoformat(data["postingDate"])
            except (ValueError, TypeError):
                pass

        value_date = None
        if "valueDate" in data and data["valueDate"]:
            try:
                value_date = datetime.fromisoformat(data["valueDate"])
            except (ValueError, TypeError):
                pass

        action_date = None
        if "actionDate" in data and data["actionDate"]:
            try:
                action_date = datetime.fromisoformat(data["actionDate"])
            except (ValueError, TypeError):
                pass

        transaction_date = None
        if "transactionDate" in data and data["transactionDate"]:
            try:
                transaction_date = datetime.fromisoformat(data["transactionDate"])
            except (ValueError, TypeError):
                pass

        # Convert numeric fields
        amount = Decimal(str(data.get("amount", 0)))
        running_balance = None
        if "runningBalance" in data and data["runningBalance"] is not None:
            running_balance = Decimal(str(data["runningBalance"]))

        return cls(
            account_id=data.get("accountId", ""),
            type=data.get("type", TransactionType.DEBIT),
            transaction_type=data.get("transactionType"),
            status=data.get("status", TransactionStatus.POSTED),
            description=data.get("description", ""),
            card_number=data.get("cardNumber"),
            posted_order=data.get("postedOrder"),
            posting_date=posting_date,
            value_date=value_date,
            action_date=action_date,
            transaction_date=transaction_date,
            amount=amount,
            running_balance=running_balance,
            uuid=data.get("uuid"),
        )


class PendingTransaction(BaseModel):
    """Pending transaction information for an Investec bank account."""

    account_id: str
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    description: str
    transaction_date: Optional[datetime] = None
    amount: Decimal

    @classmethod
    def from_dict(cls, data: dict) -> "PendingTransaction":
        """Create a PendingTransaction instance from API response data."""
        # Convert string date to datetime object if present
        transaction_date = None
        if "transactionDate" in data and data["transactionDate"]:
            try:
                transaction_date = datetime.fromisoformat(data["transactionDate"])
            except (ValueError, TypeError):
                pass

        # Convert numeric fields
        amount = Decimal(str(data.get("amount", 0)))

        return cls(
            account_id=data.get("accountId", ""),
            type=data.get("type", TransactionType.DEBIT),
            status=TransactionStatus.PENDING,
            description=data.get("description", ""),
            transaction_date=transaction_date,
            amount=amount,
        )
