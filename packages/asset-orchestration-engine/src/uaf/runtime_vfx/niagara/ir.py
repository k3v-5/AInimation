"""
UAF-81.84.10: UAF VFX Intermediate Representation (IR).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class VFXIRModule:
    """IR representation of a simulation or spawn module."""
    module_name: str
    stage: str  # Spawn, Update, Event, Collision
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VFXIRRenderer:
    """IR representation of a presentation renderer."""
    renderer_type: str  # Sprite, Mesh, Ribbon, Trail, Beam, Decal
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VFXIREmitter:
    """IR representation of an emitter with its modules and renderer."""
    emitter_id: str
    sim_target: str  # CPU, GPU
    spawn_mode: str
    max_capacity: int
    modules: Tuple[VFXIRModule, ...] = field(default_factory=tuple)
    renderer: Optional[VFXIRRenderer] = None


@dataclass(frozen=True)
class VFXIRSystem:
    """IR representation of a complete VFX System."""
    system_id: str
    revision: int = 1
    parameters: Dict[str, Any] = field(default_factory=dict)
    emitters: Tuple[VFXIREmitter, ...] = field(default_factory=tuple)

    def compute_hash(self) -> str:
        """Compute canonical SHA-256 hash of IR system."""
        emitters_data = []
        for em in self.emitters:
            mods = [{"name": m.module_name, "stage": m.stage, "params": m.parameters} for m in em.modules]
            rend = {"type": em.renderer.renderer_type, "settings": em.renderer.settings} if em.renderer else None
            emitters_data.append({
                "id": em.emitter_id,
                "sim": em.sim_target,
                "spawn": em.spawn_mode,
                "cap": em.max_capacity,
                "modules": mods,
                "renderer": rend,
            })
        payload = {
            "id": self.system_id,
            "rev": self.revision,
            "params": {k: str(v) for k, v in sorted(self.parameters.items())},
            "emitters": emitters_data,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
