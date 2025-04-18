"""Document models for the Investec API."""

from datetime import date
from typing import Any, Dict

from investec_api.models.base import BaseModel


class Document(BaseModel):
    """Investec document information."""

    document_type: str
    document_date: date

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create a Document instance from API response data."""
        # Convert string date to date object
        doc_date = None
        if "documentDate" in data and data["documentDate"]:
            try:
                doc_date = date.fromisoformat(data["documentDate"])
            except (ValueError, TypeError):
                pass

        if not doc_date:
            doc_date = date.today()

        return cls(
            document_type=data.get("documentType", ""),
            document_date=doc_date,
        )
