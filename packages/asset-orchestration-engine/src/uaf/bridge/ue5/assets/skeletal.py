"""Skeletal Mesh bridge for bone hierarchies, bind poses, and sockets."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BoneNode:
    name: str
    parent_name: Optional[str] = None
    bind_translation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    bind_rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])  # Quaternion
    bind_scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])


@dataclass
class SocketData:
    name: str
    bone_name: str
    relative_offset: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])


@dataclass
class SkeletalMeshBridgePayload:
    asset_id: str
    semantic_name: str
    bones: List[BoneNode] = field(default_factory=list)
    sockets: List[SocketData] = field(default_factory=list)
    morph_targets: List[str] = field(default_factory=list)
    has_physics_asset: bool = True
    material_slots: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "semantic_name": self.semantic_name,
            "bones": [
                {
                    "name": b.name,
                    "parent_name": b.parent_name,
                    "bind_translation": b.bind_translation,
                    "bind_rotation": b.bind_rotation,
                    "bind_scale": b.bind_scale,
                }
                for b in self.bones
            ],
            "sockets": [
                {
                    "name": s.name,
                    "bone_name": s.bone_name,
                    "relative_offset": s.relative_offset,
                }
                for s in self.sockets
            ],
            "morph_targets": self.morph_targets,
            "has_physics_asset": self.has_physics_asset,
            "material_slots": self.material_slots,
        }
