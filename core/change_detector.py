from dataclasses import dataclass
from typing import List, Optional
from models.incident import Incident
from core.state_manager import StateManager


@dataclass
class IncidentEvent:
    event_type: str            # "new" or "update"
    incident: Incident         # latest version
    previous_incident: Optional[Incident] = None  # only set for "update" events


class ChangeDetector:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    async def detect(self, incidents: List[Incident]) -> List[IncidentEvent]:
        """
        Compare incoming incidents against stored state.
        Returns a list of IncidentEvents for anything that is new or updated.
        """
        events = []

        for incident in incidents:
            if self.state_manager.is_new(incident):
                event = self._handle_new(incident)
                events.append(event)

            elif self.state_manager.is_updated(incident):
                event = self._handle_update(incident)
                events.append(event)

            # Always upsert — keeps state current even for unchanged incidents
            self.state_manager.upsert(incident)

        return events

    def _handle_new(self, incident: Incident) -> IncidentEvent:
        print(f"[ChangeDetector] NEW incident detected: '{incident.title}' from {incident.source_provider}")
        return IncidentEvent(
            event_type="new",
            incident=incident,
            previous_incident=None
        )

    def _handle_update(self, incident: Incident) -> IncidentEvent:
        previous = self.state_manager.get_existing(incident)
        print(f"[ChangeDetector] UPDATE detected on: '{incident.title}' from {incident.source_provider}")
        print(f"[ChangeDetector] Status changed: '{previous.status}' → '{incident.status}'")
        return IncidentEvent(
            event_type="update",
            incident=incident,
            previous_incident=previous
        )