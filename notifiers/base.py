from abc import ABC, abstractmethod
from core.change_detector import IncidentEvent


class BaseNotifier(ABC):

    @abstractmethod
    async def notify(self, event: IncidentEvent) -> None:
        """
        Handle an incident event.
        All notifiers must implement this method.
        """
        pass