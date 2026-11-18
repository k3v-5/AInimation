"""Evidence package preserving all audit artifacts, traces, and metrics."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EvidencePackage:
    build_id: str
    logs: List[str] = field(default_factory=list)
    traces: List[Dict[str, Any]] = field(default_factory=list)
    screenshot_hashes: Dict[str, str] = field(default_factory=dict)
    profiling_captures: Dict[str, Any] = field(default_factory=dict)
    test_results: Dict[str, Any] = field(default_factory=dict)
    replays: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "build_id": self.build_id,
            "logs_count": len(self.logs),
            "traces_count": len(self.traces),
            "screenshot_hashes": self.screenshot_hashes,
            "profiling_captures": self.profiling_captures,
            "test_results": self.test_results,
            "replays_count": len(self.replays),
        }
