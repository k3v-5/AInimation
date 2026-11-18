"""
TargetProfile declares engine features, platform constraints, and format conventions.
UAF-81.1 Sections 30, 31.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass(frozen=True)
class TargetProfile:
    """
    Target deployment profile (e.g. Unreal Engine 5.5, Unity, Blender, WebGL, Mobile).
    """
    target_id: str
    engine_name: str = "generic"
    engine_version: str = "1.0.0"
    supports_nanite: bool = False
    supports_lumen: bool = False
    supports_virtual_textures: bool = False
    preferred_mesh_format: str = "GLTF"  # GLTF, FBX, USD, OBJ
    preferred_texture_format: str = "PNG"  # PNG, TGA, EXR, DDS
    up_axis: str = "Z"  # Y or Z
    unit_scale: float = 1.0  # 1.0 = meters, 100.0 = cm (Unreal Units)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "supports_nanite": self.supports_nanite,
            "supports_lumen": self.supports_lumen,
            "supports_virtual_textures": self.supports_virtual_textures,
            "preferred_mesh_format": self.preferred_mesh_format,
            "preferred_texture_format": self.preferred_texture_format,
            "up_axis": self.up_axis,
            "unit_scale": self.unit_scale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TargetProfile":
        return cls(
            target_id=data["target_id"],
            engine_name=data.get("engine_name", "generic"),
            engine_version=data.get("engine_version", "1.0.0"),
            supports_nanite=bool(data.get("supports_nanite", False)),
            supports_lumen=bool(data.get("supports_lumen", False)),
            supports_virtual_textures=bool(data.get("supports_virtual_textures", False)),
            preferred_mesh_format=data.get("preferred_mesh_format", "GLTF"),
            preferred_texture_format=data.get("preferred_texture_format", "PNG"),
            up_axis=data.get("up_axis", "Z"),
            unit_scale=float(data.get("unit_scale", 1.0)),
        )
