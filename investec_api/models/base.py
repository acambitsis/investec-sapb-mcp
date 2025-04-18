"""Base model class for all API models."""

from datetime import datetime
from typing import Any, Dict, List, Type, TypeVar, get_type_hints

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """Base model class for all API models with JSON conversion capabilities."""

    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a model instance from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in get_type_hints(cls)})

    @classmethod
    def from_api_response(cls: Type[T], response: Dict[str, Any]) -> T:
        """Create a model instance from an API response."""
        if "data" in response:
            return cls.from_dict(response["data"])
        return cls.from_dict(response)

    @classmethod
    def list_from_api_response(
        cls: Type[T], response: Dict[str, Any], key: str
    ) -> List[T]:
        """Create a list of model instances from an API response."""
        if "data" in response and key in response["data"]:
            return [cls.from_dict(item) for item in response["data"][key]]
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to a dictionary."""
        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                result[key] = [item.to_dict() for item in value]
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
