import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class OrchestrationEvent:
    event_id: str
    orchestration_id: str
    event_type: str
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    status: str = "INFO"
    timestamp: float = field(default_factory=time.time)
    payload: Dict[str, Any] = field(default_factory=dict)

class OrchestrationEventLog:
    def __init__(self):
        self._events: List[OrchestrationEvent] = []

    def record(self, event: OrchestrationEvent):
        self._events.append(event)

    def list_events(self, orchestration_id: Optional[str] = None) -> List[OrchestrationEvent]:
        if orchestration_id:
            return [e for e in self._events if e.orchestration_id == orchestration_id]
        return list(self._events)
