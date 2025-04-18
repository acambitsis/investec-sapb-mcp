"""Payment models for the Investec API."""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from investec_api.models.base import BaseModel


class BeneficiaryPaymentItem(BaseModel):
    """Individual payment item for beneficiary payments."""

    beneficiary_id: str
    amount: Decimal
    my_reference: str
    their_reference: str
    authoriser_a_id: Optional[str] = None
    authoriser_b_id: Optional[str] = None
    auth_period_id: Optional[str] = None
    faster_payment: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dictionary."""
        result: Dict[str, Any] = {
            "beneficiaryId": self.beneficiary_id,
            "amount": str(self.amount),
            "myReference": self.my_reference,
            "theirReference": self.their_reference,
        }
        if self.authoriser_a_id:
            result["authoriserAId"] = self.authoriser_a_id
        if self.authoriser_b_id:
            result["authoriserBId"] = self.authoriser_b_id
        if self.auth_period_id:
            result["authPeriodId"] = self.auth_period_id
        if self.faster_payment is not None:
            result["fasterPayment"] = self.faster_payment
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BeneficiaryPaymentItem":
        """Create a BeneficiaryPaymentItem instance from dictionary data."""
        return cls(
            beneficiary_id=data.get("beneficiaryId", ""),
            amount=Decimal(str(data.get("amount", 0))),
            my_reference=data.get("myReference", ""),
            their_reference=data.get("theirReference", ""),
            authoriser_a_id=data.get("authoriserAId"),
            authoriser_b_id=data.get("authoriserBId"),
            auth_period_id=data.get("authPeriodId"),
            faster_payment=data.get("fasterPayment"),
        )


class BeneficiaryPaymentRequest(BaseModel):
    """Request model for beneficiary payments."""

    payment_list: List[BeneficiaryPaymentItem]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dictionary."""
        return {
            "paymentList": [item.to_dict() for item in self.payment_list],
        }


class PaymentResponseItem(BaseModel):
    """Individual payment response for beneficiary payments."""

    payment_reference_number: Optional[str] = None
    payment_date: Optional[str] = None
    status: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_account_id: Optional[str] = None
    authorisation_required: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentResponseItem":
        """Create a PaymentResponseItem instance from API response data."""
        return cls(
            payment_reference_number=data.get("PaymentReferenceNumber"),
            payment_date=data.get("PaymentDate"),
            status=data.get("Status"),
            beneficiary_name=data.get("BeneficiaryName"),
            beneficiary_account_id=data.get("BeneficiaryAccountId"),
            authorisation_required=data.get("AuthorisationRequired", False),
        )


class PaymentResponse(BaseModel):
    """Response model for beneficiary payments."""

    transfer_responses: List[PaymentResponseItem]
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentResponse":
        """Create a PaymentResponse instance from API response data."""
        transfer_responses = []

        # Access the TransferResponses array
        responses = []
        if "TransferResponses" in data:
            responses = data["TransferResponses"]

        for item in responses:
            transfer_responses.append(PaymentResponseItem.from_dict(item))

        return cls(
            transfer_responses=transfer_responses,
            error_message=data.get("ErrorMessage"),
        )
