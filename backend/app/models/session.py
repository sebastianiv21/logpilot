"""Session domain model."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=False)
class Session:
    """Logical container for an investigation. id, created_at, updated_at required."""

    id: str
    name: str | None
    external_link: str | None
    created_at: str
    updated_at: str

    def to_api(self) -> dict[str, Any]:
        """API response shape: id, name, external_link, created_at, updated_at."""
        return {
            "id": self.id,
            "name": self.name,
            "external_link": self.external_link,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
