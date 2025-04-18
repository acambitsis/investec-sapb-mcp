"""Transfer models for the Investec API."""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from investec_api.models.base import BaseModel


class TransferItem(BaseModel):
    """Individual transfer item for inter-account transfers."""

    beneficiary_account_id: str
    amount: Decimal
    my_reference: str
    their_reference: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dictionary."""
        return {
            "beneficiaryAccountId": self.beneficiary_account_id,
            "amount": str(self.amount),
            "myReference": self.my_reference,
            "theirReference": self.their_reference,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferItem":
        """Create a TransferItem instance from dictionary data."""
        return cls(
            beneficiary_account_id=data.get("beneficiaryAccountId", ""),
            amount=Decimal(str(data.get("amount", 0))),
            my_reference=data.get("myReference", ""),
            their_reference=data.get("theirReference", ""),
        )


class TransferRequest(BaseModel):
    """Request model for inter-account transfers."""

    transfer_list: List[TransferItem]
    profile_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dictionary."""
        result: Dict[str, Any] = {
            "transferList": [item.to_dict() for item in self.transfer_list],
        }
        if self.profile_id:
            result["profileId"] = self.profile_id
        return result


class TransferResponseItem(BaseModel):
    """Individual transfer response for inter-account transfers."""

    payment_reference_number: Optional[str] = None
    payment_date: Optional[str] = None
    status: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_account_id: Optional[str] = None
    authorisation_required: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferResponseItem":
        """Create a TransferResponseItem instance from API response data."""
        return cls(
            payment_reference_number=data.get("PaymentReferenceNumber"),
            payment_date=data.get("PaymentDate"),
            status=data.get("Status"),
            beneficiary_name=data.get("BeneficiaryName"),
            beneficiary_account_id=data.get("BeneficiaryAccountId"),
            authorisation_required=data.get("AuthorisationRequired", False),
        )


class TransferResponse(BaseModel):
    """Response model for inter-account transfers."""

    transfer_responses: List[TransferResponseItem]
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferResponse":
        """Create a TransferResponse instance from API response data."""
        transfer_responses = []

        # Handle both v1 and v2 API response formats
        responses = []
        if (
            "transferResponse" in data
            and "TransferResponses" in data["transferResponse"]
        ):
            responses = data["transferResponse"]["TransferResponses"]
        elif "TransferResponses" in data:
            responses = data["TransferResponses"]

        for item in responses:
            transfer_responses.append(TransferResponseItem.from_dict(item))

        error_message = None
        if "transferResponse" in data and "ErrorMessage" in data["transferResponse"]:
            error_message = data["transferResponse"]["ErrorMessage"]
        elif "ErrorMessage" in data:
            error_message = data["ErrorMessage"]

        return cls(
            transfer_responses=transfer_responses,
            error_message=error_message,
        )
