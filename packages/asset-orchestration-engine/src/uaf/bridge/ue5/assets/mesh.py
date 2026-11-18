"""Static Mesh bridge for geometry translation, Nanite flags, and LODs."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MeshLODData:
    lod_index: int
    triangle_count: int
    vertex_count: int
    screen_size: float = 1.0


@dataclass
class StaticMeshBridgePayload:
    asset_id: str
    semantic_name: str
    lods: List[MeshLODData] = field(default_factory=list)
    material_slots: List[str] = field(default_factory=list)
    enable_nanite: bool = True
    generate_collision: bool = True
    collision_complexity: str = "UseSimpleAndComplex"
    uv_channel_count: int = 1
    has_vertex_colors: bool = False
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "semantic_name": self.semantic_name,
            "lods": [
                {
                    "lod_index": lod.lod_index,
                    "triangle_count": lod.triangle_count,
                    "vertex_count": lod.vertex_count,
                    "screen_size": lod.screen_size,
                }
                for lod in self.lods
            ],
            "material_slots": self.material_slots,
            "enable_nanite": self.enable_nanite,
            "generate_collision": self.generate_collision,
            "collision_complexity": self.collision_complexity,
            "uv_channel_count": self.uv_channel_count,
            "has_vertex_colors": self.has_vertex_colors,
            "custom_properties": self.custom_properties,
        }
