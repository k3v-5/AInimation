import time
from typing import Dict, List, Callable, Any
from ..core.runtime_types import RuntimeEventType
from ..core.runtime_schema import EventEnvelope

class EventBus:
    def __init__(self):
        self._subscribers: Dict[RuntimeEventType, List[Callable[[EventEnvelope], None]]] = {}
        self.persistent_events: List[EventEnvelope] = []

    def subscribe(self, event_type: RuntimeEventType, callback: Callable[[EventEnvelope], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: RuntimeEventType, task_id: str, asset_id: str, payload: Dict[str, Any], source: str = "SYSTEM", correlation_id: str = "") -> EventEnvelope:
        event = EventEnvelope(
            event_id=f"EVT_{int(time.time()*1000)}_{len(self.persistent_events)}",
            event_type=event_type,
            timestamp=time.time(),
            source=source,
            task_id=task_id,
            asset_id=asset_id,
            payload=payload,
            correlation_id=correlation_id or task_id
        )
        self.persistent_events.append(event)
        
        # Notificar suscriptores
        if event_type in self._subscribers:
            for cb in self._subscribers[event_type]:
                try:
                    cb(event)
                except Exception:
                    pass
        return event

    def replay(self) -> List[EventEnvelope]:
        """Reconstruye el historial de eventos persistentes."""
        return list(self.persistent_events)
