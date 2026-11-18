"""
Universal Character Package & ProductionReadyCharacter for Unreal Engine.
UAF-81.54 Sections 2, 176, 177.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    CharacterDefinition,
    BodyComponent,
    SkeletonDefinition,
    RigDefinition,
    SkinningDefinition,
    DeformationProfile,
    MorphTargetSystem,
    ClothingDefinition,
    ArmorDefinition,
    AccessoryDefinition,
    HairDefinition,
    CharacterCollisionDefinition,
    CharacterLODChain,
    RetargetProfile,
)
from ..validation.universal_character_validator import CharacterValidationReport


@dataclass
class ProductionReadyCharacter:
    """
    Complete production asset representing a rigged, skinned, deformed character ready for Unreal Engine (Section 2, 176).
    """
    character_def: CharacterDefinition
    skeleton: SkeletonDefinition
    rig: RigDefinition
    skinning: SkinningDefinition
    deformation: DeformationProfile
    morphs: MorphTargetSystem
    components: List[BodyComponent] = field(default_factory=list)
    clothing: List[ClothingDefinition] = field(default_factory=list)
    armor: List[ArmorDefinition] = field(default_factory=list)
    accessories: List[AccessoryDefinition] = field(default_factory=list)
    hair: Optional[HairDefinition] = None
    collision: CharacterCollisionDefinition = field(default_factory=lambda: CharacterCollisionDefinition("Col_01"))
    lod_chain: CharacterLODChain = field(default_factory=CharacterLODChain)
    retarget: Optional[RetargetProfile] = None
    validation_report: Optional[CharacterValidationReport] = None

    # Unreal Asset Paths
    skeletal_mesh_path: str = "/Game/Characters/SK_Character.uasset"
    skeleton_path: str = "/Game/Characters/SKEL_Character.uasset"
    physics_asset_path: str = "/Game/Characters/PHYS_Character.uasset"

    # Mesh Geometry stats
    vertex_count: int = 1200
    triangle_count: int = 2400
    material_slots: List[str] = field(default_factory=lambda: ["M_Body", "M_Clothing"])
    bounds: Dict[str, float] = field(default_factory=lambda: {"min_z": 0.0, "max_z": 180.0, "width": 60.0})

    @property
    def canonical_hash(self) -> str:
        payload = {
            "character_id": self.character_def.character_id,
            "species": self.character_def.species.value,
            "archetype": self.character_def.archetype.value,
            "seed": self.character_def.seed,
            "bone_count": len(self.skeleton.bones),
            "bone_names": self.skeleton.bone_names,
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "skeletal_mesh_path": self.skeletal_mesh_path,
        }
        return CanonicalHasher.compute_hash(payload)

    def verify_readback(self) -> Dict[str, Any]:
        """
        Post-export / import readback validation checking structural integrity (Section 177).
        """
        return {
            "bone_count": len(self.skeleton.bones),
            "bone_names": self.skeleton.bone_names,
            "hierarchy_valid": not self.skeleton.has_cyclic_hierarchy(),
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "weight_count": len(self.skinning.weights_per_vertex),
            "material_slots": self.material_slots,
            "morph_count": len(self.morphs.morphs),
            "socket_count": sum(len(c.attachment_points) for c in self.components),
            "lod_count": self.lod_chain.lod_count,
            "bounds": self.bounds,
            "readback_passed": (
                len(self.skeleton.bones) > 0 and
                self.vertex_count > 0 and
                self.triangle_count > 0 and
                not self.skeleton.has_cyclic_hierarchy()
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_identity": self.character_def.to_dict(),
            "skeleton": self.skeleton.to_dict(),
            "rig": self.rig.to_dict(),
            "skinning": self.skinning.to_dict(),
            "deformation": self.deformation.to_dict(),
            "morphs": self.morphs.to_dict(),
            "components": [c.to_dict() for c in self.components],
            "clothing": [cl.to_dict() for cl in self.clothing],
            "armor": [ar.to_dict() for ar in self.armor],
            "accessories": [ac.to_dict() for ac in self.accessories],
            "hair": self.hair.to_dict() if self.hair else None,
            "collision": self.collision.to_dict(),
            "lod": self.lod_chain.to_dict(),
            "retarget": self.retarget.to_dict() if self.retarget else None,
            "validation": self.validation_report.to_dict() if self.validation_report else None,
            "export_metadata": {
                "skeletal_mesh_path": self.skeletal_mesh_path,
                "skeleton_path": self.skeleton_path,
                "physics_asset_path": self.physics_asset_path,
                "canonical_hash": self.canonical_hash,
            }
        }


# Alias for consistency with other UAF packages
UniversalCharacterPackage = ProductionReadyCharacter
