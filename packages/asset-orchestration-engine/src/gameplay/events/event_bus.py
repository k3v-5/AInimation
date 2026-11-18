from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Tuple, Optional

@dataclass
class GameplayEvent:
    event_name: str
    source_actor_id: str
    target_actor_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

class EventBus:
    def __init__(self, max_depth: int = 32):
        self.max_depth = max_depth
        self.listeners: Dict[str, List[Callable[[GameplayEvent], None]]] = {}
        self.event_history: List[GameplayEvent] = []

    def subscribe(self, event_name: str, callback: Callable[[GameplayEvent], None]):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def publish(self, event: GameplayEvent, current_depth: int = 1) -> Tuple[bool, Optional[str]]:
        if current_depth > self.max_depth:
            return False, f"EVENT_CHAIN_LIMIT: Maximum event recursion depth of {self.max_depth} exceeded."

        self.event_history.append(event)
        callbacks = self.listeners.get(event.event_name, [])
        for cb in callbacks:
            cb(event)

        return True, None
