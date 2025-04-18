"""Profile models for the Investec API."""

from typing import Any, Dict, List

from investec_api.models.base import BaseModel


class Profile(BaseModel):
    """Investec profile information."""

    profile_id: str
    profile_name: str
    default_profile: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        """Create a Profile instance from API response data."""
        return cls(
            profile_id=data.get("profileId", ""),
            profile_name=data.get("profileName", ""),
            default_profile=data.get("defaultProfile", False),
        )


class AuthorisationPeriod(BaseModel):
    """Period for authorization of payments."""

    id: str
    description: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorisationPeriod":
        """Create an AuthorisationPeriod instance from API response data."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
        )


class Authoriser(BaseModel):
    """Authoriser information for payments requiring authorization."""

    authoriser_id: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Authoriser":
        """Create an Authoriser instance from API response data."""
        return cls(
            authoriser_id=data.get("authoriserId", ""),
            name=data.get("name", ""),
        )


class AuthorisationSetup(BaseModel):
    """Authorisation setup information for an account."""

    number_of_authorisation_required: str
    period: List[AuthorisationPeriod]
    authorisers_list_a: List[Authoriser]
    authorisers_list_b: List[Authoriser]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorisationSetup":
        """Create an AuthorisationSetup instance from API response data."""
        periods: List[AuthorisationPeriod] = []
        for period_data in data.get("period", []):
            periods.append(AuthorisationPeriod.from_dict(period_data))

        authorisers_a: List[Authoriser] = []
        for auth_data in data.get("authorisersListA", []):
            authorisers_a.append(Authoriser.from_dict(auth_data))

        authorisers_b: List[Authoriser] = []
        for auth_data in data.get("authorisersListB", []):
            authorisers_b.append(Authoriser.from_dict(auth_data))

        return cls(
            number_of_authorisation_required=data.get(
                "numberOfAuthorisationRequired", ""
            ),
            period=periods,
            authorisers_list_a=authorisers_a,
            authorisers_list_b=authorisers_b,
        )
