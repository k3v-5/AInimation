"""Failure artifact capturing contextual forensic data for automated analysis."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FailureArtifact:
    failure_id: str = field(default_factory=lambda: f"fail_{uuid.uuid4().hex[:10]}")
    build_id: str = ""
    scenario: str = ""
    frame: int = 0
    subsystem: str = "General"
    error: str = ""
    stack: str = ""
    state_hash: str = ""
    trace: List[Dict[str, Any]] = field(default_factory=list)
    reproduction_steps: List[str] = field(default_factory=list)
    repair_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)
