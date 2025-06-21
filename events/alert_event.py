from pmevents import PMEvent
from dataclasses import dataclass

@dataclass
class AlertEvent(PMEvent):
	message: str
	timeout: int
