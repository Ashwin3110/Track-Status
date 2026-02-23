import json
import os
import aiofiles
from typing import Dict, Optional
from models.incident import Incident


STATE_FILE_PATH = "state.json"


class StateManager:
    def __init__(self):
        # In-memory state:
        # { provider_name: { incident_id: Incident } }
        self._state: Dict[str, Dict[str, Incident]] = {}

    async def load(self):
        """Load state from disk into memory on startup."""
        if not os.path.exists(STATE_FILE_PATH):
            print("[StateManager] No existing state file found. Starting fresh.")
            self._state = {}
            return

        try:
            async with aiofiles.open(STATE_FILE_PATH, "r") as f:
                raw = await f.read()
                data = json.loads(raw)

            # Deserialize each incident dict back into an Incident object
            for provider, incidents in data.items():
                self._state[provider] = {}
                for incident_id, incident_dict in incidents.items():
                    self._state[provider][incident_id] = Incident.from_dict(incident_dict)

            total = sum(len(v) for v in self._state.values())
            print(f"[StateManager] Loaded {total} incidents from state file.")

        except Exception as e:
            print(f"[StateManager] Failed to load state file: {e}. Starting fresh.")
            self._state = {}

    async def save(self):
        """Persist current in-memory state to disk."""
        try:
            # Serialize all Incident objects to plain dicts
            serializable = {}
            for provider, incidents in self._state.items():
                serializable[provider] = {
                    incident_id: incident.to_dict()
                    for incident_id, incident in incidents.items()
                }

            async with aiofiles.open(STATE_FILE_PATH, "w") as f:
                await f.write(json.dumps(serializable, indent=2))

        except Exception as e:
            print(f"[StateManager] Failed to save state: {e}")

    def is_new(self, incident: Incident) -> bool:
        """Returns True if this incident has never been seen before."""
        provider_state = self._state.get(incident.source_provider, {})
        return incident.incident_id not in provider_state

    def is_updated(self, incident: Incident) -> bool:
        """Returns True if this incident exists but has a newer updated_at timestamp."""
        provider_state = self._state.get(incident.source_provider, {})
        existing = provider_state.get(incident.incident_id)
        if existing is None:
            return False
        return incident.updated_at != existing.updated_at

    def get_existing(self, incident: Incident) -> Optional[Incident]:
        """Returns the stored version of an incident, or None if not found."""
        return self._state.get(incident.source_provider, {}).get(incident.incident_id)

    def upsert(self, incident: Incident):
        """Insert a new incident or update an existing one in memory."""
        if incident.source_provider not in self._state:
            self._state[incident.source_provider] = {}
        self._state[incident.source_provider][incident.incident_id] = incident