"""
QualityProfile dictates technical fidelity targets (LODs, texture sizes, polygon budgets).
UAF-81.1 Section 29.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class QualityProfile:
    """
    Fidelity constraints controlling target resolutions, polycounts, and texture budgets.
    """
    profile_id: str  # e.g., "preview", "standard", "production", "hero", "cinematic"
    max_polycount: int = 100000
    target_texture_resolution: int = 2048
    enable_lod_chain: bool = True
    lod_count: int = 4
    enable_nanite: bool = False
    shadow_caster: bool = True
    raytracing_ready: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "max_polycount": self.max_polycount,
            "target_texture_resolution": self.target_texture_resolution,
            "enable_lod_chain": self.enable_lod_chain,
            "lod_count": self.lod_count,
            "enable_nanite": self.enable_nanite,
            "shadow_caster": self.shadow_caster,
            "raytracing_ready": self.raytracing_ready,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityProfile":
        return cls(
            profile_id=data["profile_id"],
            max_polycount=int(data.get("max_polycount", 100000)),
            target_texture_resolution=int(data.get("target_texture_resolution", 2048)),
            enable_lod_chain=bool(data.get("enable_lod_chain", True)),
            lod_count=int(data.get("lod_count", 4)),
            enable_nanite=bool(data.get("enable_nanite", False)),
            shadow_caster=bool(data.get("shadow_caster", True)),
            raytracing_ready=bool(data.get("raytracing_ready", False)),
        )
