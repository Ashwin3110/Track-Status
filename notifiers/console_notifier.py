from core.change_detector import IncidentEvent
from notifiers.base import BaseNotifier


class ConsoleNotifier(BaseNotifier):

    async def notify(self, event: IncidentEvent) -> None:
        if event.event_type == "new":
            self._print_new(event)
        elif event.event_type == "update":
            self._print_update(event)

    def _print_new(self, event: IncidentEvent) -> None:
        inc = event.incident
        print("\n" + "=" * 60)
        print(f"NEW INCIDENT DETECTED")
        print("=" * 60)
        print(f"  Provider  : {inc.source_provider}")
        print(f"  Title     : {inc.title}")
        print(f"  Status    : {inc.status}")
        print(f"  Services  : {', '.join(inc.affected_services) if inc.affected_services else 'Unknown'}")
        print(f"  Message   : {inc.latest_message}")
        print(f"  Updated   : {inc.updated_at}")
        print(f"  URL       : {inc.incident_url}")
        print("=" * 60 + "\n")

    def _print_update(self, event: IncidentEvent) -> None:
        inc = event.incident
        prev = event.previous_incident
        print("\n" + "-" * 60)
        print(f"INCIDENT UPDATED")
        print("-" * 60)
        print(f"  Provider  : {inc.source_provider}")
        print(f"  Title     : {inc.title}")
        print(f"  Status    : {prev.status} → {inc.status}")
        print(f"  Services  : {', '.join(inc.affected_services) if inc.affected_services else 'Unknown'}")
        print(f"  Message   : {inc.latest_message}")
        print(f"  Updated   : {inc.updated_at}")
        print(f"  URL       : {inc.incident_url}")
        print("-" * 60 + "\n")