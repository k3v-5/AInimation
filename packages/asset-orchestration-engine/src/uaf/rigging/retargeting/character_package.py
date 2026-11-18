"""
UnrealCharacterPackage encapsulates ready-to-import skeletal mesh, rig, skinning, and physics assets.
UAF-81.5 Section 80.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..skeleton.skeleton_definition import CharacterSkeletonDefinition
from ..rig.rig_definition import RigDefinition
from ..skinning.skinning_definition import SkinningDefinition
from ..facial.facial_rig import FacialRigDefinition
from ..physics.physics_asset import PhysicsAssetDefinition
from .retarget_profile import RetargetProfile
from ...geometry.models.geometry_component import GeometryComponent


@dataclass
class UnrealCharacterPackage:
    asset_id: str
    skeleton: CharacterSkeletonDefinition
    rig: RigDefinition
    skinning: SkinningDefinition
    physics: PhysicsAssetDefinition
    retarget_profile: RetargetProfile
    geometry: Optional[GeometryComponent] = None
    facial: Optional[FacialRigDefinition] = None
    validation_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "skeleton": self.skeleton.to_dict(),
            "rig": self.rig.to_dict(),
            "skinning": self.skinning.to_dict(),
            "physics": self.physics.to_dict(),
            "retarget_profile": self.retarget_profile.to_dict(),
            "geometry": self.geometry.to_dict() if self.geometry else None,
            "facial": self.facial.to_dict() if self.facial else None,
            "validation_status": self.validation_status,
            "metadata": self.metadata,
        }
