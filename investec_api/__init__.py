"""
Investec API Python Client

A typed Python wrapper for the Investec Open Banking API.
"""

from investec_api.client import InvestecClient
from investec_api.exceptions import (
    InvestecAPIError,
    InvestecAuthError,
    InvestecRateLimitError,
    InvestecRequestError,
)
from investec_api.models import (
    Account,
    AccountBalance,
    Beneficiary,
    BeneficiaryCategory,
    BeneficiaryPaymentRequest,
    Document,
    Profile,
    Transaction,
    TransferRequest,
    TransferResponse,
)

__version__ = "0.1.0"

__all__ = [
    "InvestecClient",
    "InvestecAPIError",
    "InvestecAuthError",
    "InvestecRequestError",
    "InvestecRateLimitError",
    "Account",
    "AccountBalance",
    "Transaction",
    "Beneficiary",
    "TransferRequest",
    "TransferResponse",
    "BeneficiaryPaymentRequest",
    "BeneficiaryCategory",
    "Profile",
    "Document",
]
