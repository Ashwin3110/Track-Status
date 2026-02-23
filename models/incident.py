# This file will contain a single Python dataclass that represents one normalized incident. 
# A dataclass is the right choice here because:
    # It's lightweight and built into Python (no extra library)
    # It gives you a clean, readable structure
    # It's easy to serialize to/from JSON for state persistence

from dataclasses import dataclass, field
from typing import List


@dataclass
class Incident:
    incident_id: str
    title: str
    status: str
    affected_services: List[str]
    latest_message: str
    updated_at: str
    source_provider: str
    incident_url: str

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "status": self.status,
            "affected_services": self.affected_services,
            "latest_message": self.latest_message,
            "updated_at": self.updated_at,
            "source_provider": self.source_provider,
            "incident_url": self.incident_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Incident":
        return cls(
            incident_id=data["incident_id"],
            title=data["title"],
            status=data["status"],
            affected_services=data["affected_services"],
            latest_message=data["latest_message"],
            updated_at=data["updated_at"],
            source_provider=data["source_provider"],
            incident_url=data["incident_url"],
        )