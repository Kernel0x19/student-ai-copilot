from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class RawOpportunity:
    external_id: str
    source: str
    title: str
    description: str = ""
    amount_min: float | None = None
    amount_max: float | None = None
    deadline: date | None = None
    eligibility_rules: dict = field(default_factory=dict)
    documents_required: list[str] = field(default_factory=list)
    application_url: str | None = None
    state_filter: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)


class BaseConnector(ABC):
    source_id: str

    @abstractmethod
    def fetch(self) -> list[RawOpportunity]:
        """Fetch opportunities from the source."""

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Return connector health metadata."""
