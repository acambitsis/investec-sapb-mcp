"""Beneficiary models for the Investec API."""

from typing import Optional

from investec_api.models.base import BaseModel


class Beneficiary(BaseModel):
    """Investec bank beneficiary information."""

    beneficiary_id: str
    account_number: Optional[str] = None
    code: Optional[str] = None
    bank: Optional[str] = None
    beneficiary_name: Optional[str] = None
    last_payment_amount: Optional[str] = None
    last_payment_date: Optional[str] = None
    cell_no: Optional[str] = None
    email_address: Optional[str] = None
    name: Optional[str] = None
    reference_account_number: Optional[str] = None
    reference_name: Optional[str] = None
    category_id: Optional[str] = None
    profile_id: Optional[str] = None
    faster_payment_allowed: bool = False
    beneficiary_type: Optional[str] = None
    approved_beneficiary_category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Beneficiary":
        """Create a Beneficiary instance from API response data."""
        return cls(
            beneficiary_id=data.get("beneficiaryId", ""),
            account_number=data.get("accountNumber"),
            code=data.get("code"),
            bank=data.get("bank"),
            beneficiary_name=data.get("beneficiaryName"),
            last_payment_amount=data.get("lastPaymentAmount"),
            last_payment_date=data.get("lastPaymentDate"),
            cell_no=data.get("cellNo"),
            email_address=data.get("emailAddress"),
            name=data.get("name"),
            reference_account_number=data.get("referenceAccountNumber"),
            reference_name=data.get("referenceName"),
            category_id=data.get("categoryId"),
            profile_id=data.get("profileId"),
            faster_payment_allowed=data.get("fasterPaymentAllowed", False),
            beneficiary_type=data.get("beneficiaryType"),
            approved_beneficiary_category=data.get("approvedBeneficiaryCategory"),
        )


class BeneficiaryCategory(BaseModel):
    """Investec bank beneficiary category information."""

    id: str
    is_default: bool
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "BeneficiaryCategory":
        """Create a BeneficiaryCategory instance from API response data."""
        # Convert string is_default to boolean
        is_default = False
        if "isDefault" in data:
            is_default = (
                data["isDefault"].lower() == "true"
                if isinstance(data["isDefault"], str)
                else bool(data["isDefault"])
            )

        return cls(
            id=data.get("id", ""),
            is_default=is_default,
            name=data.get("name", ""),
        )
