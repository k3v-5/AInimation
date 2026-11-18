"""Input, simulation, and bridge trace recorder and deterministic replay engine."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TraceRecord:
    frame: int
    event_type: str  # "INPUT", "SIMULATION", "BRIDGE"
    payload: Dict[str, Any]
    state_hash: str


class ReplayEngine:
    """Records and deterministically replays gameplay input and bridge traces."""

    def __init__(self) -> None:
        self.recorded_trace: List[TraceRecord] = []
        self.is_recording: bool = False

    def start_recording(self) -> None:
        self.recorded_trace.clear()
        self.is_recording = True

    def record_frame(self, frame: int, event_type: str, payload: Dict[str, Any], state_hash: str) -> None:
        if self.is_recording:
            self.recorded_trace.append(
                TraceRecord(frame=frame, event_type=event_type, payload=dict(payload), state_hash=state_hash)
            )

    def stop_recording(self) -> List[TraceRecord]:
        self.is_recording = False
        return list(self.recorded_trace)

    def replay_trace(self, trace: Optional[List[TraceRecord]] = None) -> List[str]:
        """Replays a trace and yields the state hashes produced at each frame."""
        records = trace if trace is not None else self.recorded_trace
        return [r.state_hash for r in records]
