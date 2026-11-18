"""
UE5 Live-Reload Delta Compiler for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from uaf.runtime_lighting.world import LightingWorld
from .lights import UE5LightExporter


@dataclass
class UE5LiveUpdatePacket:
    """Delta update packet for live reload in Unreal Engine 5."""
    revision: int
    added_lights: List[Dict[str, Any]] = field(default_factory=list)
    updated_lights: List[Dict[str, Any]] = field(default_factory=list)
    removed_light_ids: List[str] = field(default_factory=list)
    postprocess_updated: bool = False
    atmosphere_updated: bool = False


class UE5LightingLiveReloader:
    """
    Computes delta updates between frames and generates hot-reload commands for UE5.
    """

    def __init__(self) -> None:
        self.last_hashes: Dict[str, str] = {}
        self.revision: int = 0

    def compute_delta(self, world: LightingWorld) -> UE5LiveUpdatePacket:
        self.revision += 1
        packet = UE5LiveUpdatePacket(revision=self.revision)

        current_keys = set(world.lights.keys())
        previous_keys = set(self.last_hashes.keys())

        # Removed
        for rem in previous_keys - current_keys:
            packet.removed_light_ids.append(rem)
            self.last_hashes.pop(rem, None)

        # Added or Updated
        for key in current_keys:
            light = world.lights[key]
            h = light.compute_hash()
            if key not in previous_keys:
                packet.added_lights.append(UE5LightExporter.export_light(light))
                self.last_hashes[key] = h
            elif self.last_hashes[key] != h:
                packet.updated_lights.append(UE5LightExporter.export_light(light))
                self.last_hashes[key] = h

        return packet
