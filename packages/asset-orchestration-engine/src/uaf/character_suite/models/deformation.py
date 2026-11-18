"""
DeformationProfile, FaceProfile, and CharacterLayer models.
UAF-81.14 Sections 21, 22, 23, 24, 25, 26, 154.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class DeformationProfile:
    bone_count: int = 68
    max_weights_per_vertex: int = 4
    has_dual_quaternion: bool = True
    deformation_quality: float = 0.95

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_count": self.bone_count,
            "max_weights_per_vertex": self.max_weights_per_vertex,
            "has_dual_quaternion": self.has_dual_quaternion,
            "deformation_quality": self.deformation_quality,
        }


@dataclass
class FaceProfile:
    eye_spacing: float = 1.0
    jaw_width: float = 1.0
    nose_length: float = 1.0
    morph_targets_count: int = 52  # ARKit / Metahuman compatible expression targets

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eye_spacing": self.eye_spacing,
            "jaw_width": self.jaw_width,
            "nose_length": self.nose_length,
            "morph_targets_count": self.morph_targets_count,
        }


@dataclass
class CharacterLayer:
    layer_id: str
    layer_type: str  # "BODY", "CLOTHING", "ARMOR", "ACCESSORIES", "HAIR"
    mesh_id: str
    material_id: str
    clipping_clearance_mm: float = 2.0  # Min clearance above inner layer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_type": self.layer_type,
            "mesh_id": self.mesh_id,
            "material_id": self.material_id,
            "clipping_clearance_mm": self.clipping_clearance_mm,
        }
