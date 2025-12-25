from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"

class Notifier(ABC):
    @abstractmethod
    async def send(self, message: str, level: AlertLevel = AlertLevel.INFO) -> bool:
        """Sends a notification asynchronously."""
        pass
