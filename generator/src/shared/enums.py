from enum import Enum
from typing import Any

__all__ = ["BaseEnum"]


class BaseEnum(Enum):
    """Base enumeration class with auxiliary methods."""

    @classmethod
    def choices(cls) -> list[tuple[str, Any]]:
        """Return a list of the tuples (NAME, VALUE)."""
        return [(item.name, item.value) for item in cls]

    @classmethod
    def values(cls) -> list[Any]:
        """Return a list with only the enums values."""
        return [item.value for item in cls]

    @classmethod
    def names(cls) -> list[str]:
        """Return a list with only the enums names."""
        return [item.name for item in cls]
