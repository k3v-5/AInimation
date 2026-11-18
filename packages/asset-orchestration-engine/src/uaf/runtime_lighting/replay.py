"""
Event Recording & Replay Engine for UAF-81.85.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from .core import LightId, WeatherCondition


@dataclass
class LightingEvent:
    """Discrete causal lighting event recorded for deterministic replay."""
    frame: int
    timestamp: float
    event_type: str
    payload: Dict[str, Any]


class LightingReplayEngine:
    """
    Records and replays coarse causal lighting events (lights created, destroyed, weather changes).
    """

    def __init__(self) -> None:
        self.recorded_events: List[LightingEvent] = []
        self.is_recording: bool = True

    def record(self, frame: int, timestamp: float, event_type: str, payload: Dict[str, Any]) -> None:
        if not self.is_recording:
            return
        event = LightingEvent(
            frame=frame,
            timestamp=round(timestamp, 4),
            event_type=event_type,
            payload=payload,
        )
        self.recorded_events.append(event)

    def export_replay_log(self) -> str:
        """Serializes recorded events to JSON."""
        return json.dumps([asdict(e) for e in self.recorded_events], indent=2)

    def load_replay_log(self, json_data: str) -> None:
        """Loads events from JSON log."""
        raw_list = json.loads(json_data)
        self.recorded_events = [
            LightingEvent(
                frame=item["frame"],
                timestamp=item["timestamp"],
                event_type=item["event_type"],
                payload=item["payload"],
            )
            for item in raw_list
        ]
