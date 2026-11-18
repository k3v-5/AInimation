import time
from typing import Dict, Any, List

class EventCollector:
    """Collects and correlates operational events and traces leading up to an incident."""
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, details: Dict[str, Any], correlation_id: str = ""):
        self._events.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "correlation_id": correlation_id,
            "details": details
        })

    def get_events(self, correlation_id: str = "") -> List[Dict[str, Any]]:
        if not correlation_id:
            return list(self._events)
        return [e for e in self._events if e.get("correlation_id") == correlation_id]
