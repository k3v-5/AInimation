"""
Deterministic Snapshot & Canonical State Hashing for UAF-81.85.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .core import LightId
from .lights import Light


@dataclass
class LightingSnapshot:
    """
    Immutable state snapshot of the lighting and atmosphere runtime.
    Produces a canonical SHA-256 hash independent of GPU/memory addresses.
    """
    frame_index: int
    simulation_time: float
    world_time_seconds: float
    sun_state: Dict[str, Any]
    moon_state: Dict[str, Any]
    lights_state: List[Dict[str, Any]]
    fog_state: Dict[str, Any]
    clouds_state: Dict[str, Any]
    postprocess_state: Dict[str, Any]
    canonical_hash: str = ""

    def __post_init__(self) -> None:
        if not self.canonical_hash:
            self.canonical_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Computes deterministic SHA-256 canonical hash."""
        # Ensure lights are stably sorted by light_id
        sorted_lights = sorted(self.lights_state, key=lambda l: l.get("light_id", ""))
        payload_dict = {
            "frame_index": self.frame_index,
            "simulation_time": round(self.simulation_time, 4),
            "world_time_seconds": round(self.world_time_seconds, 2),
            "sun_state": self.sun_state,
            "moon_state": self.moon_state,
            "lights_state": sorted_lights,
            "fog_state": self.fog_state,
            "clouds_state": self.clouds_state,
            "postprocess_state": self.postprocess_state,
        }
        serialized = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
