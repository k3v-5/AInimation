"""
FormLevel, BodyComponent, and SemanticBodyGraph models.
UAF-81.10 Sections 3, 4, 6, 7, 8, 10, 11, 12.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class FormLevel(str, Enum):
    PRIMARY = "PRIMARY"          # Main silhouette and anatomical volume
    SECONDARY = "SECONDARY"      # Muscles, joints, armor plates, boots
    TERTIARY = "TERTIARY"        # Seams, vents, wrinkles, fasteners, bolts
    SURFACE = "SURFACE"          # Normal, roughness, pore, microdetail
    DEFORMATION = "DEFORMATION"  # Skinning edge-loops and bend zones
    RUNTIME = "RUNTIME"          # Optimized lod / collision representations


@dataclass
class BodyComponent:
    component_id: str
    form_level: FormLevel
    parent_id: Optional[str] = None
    material_region_id: str = "MAT_SKIN"
    is_rigid: bool = False       # True for hard-surface/mechanical, False for organic/deforming
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "form_level": self.form_level.value,
            "parent_id": self.parent_id,
            "material_region_id": self.material_region_id,
            "is_rigid": self.is_rigid,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "metadata": self.metadata,
        }


@dataclass
class SemanticBodyGraph:
    character_id: str
    components: Dict[str, BodyComponent] = field(default_factory=dict)

    def add_component(self, component: BodyComponent) -> None:
        self.components[component.component_id] = component

    def get_components_by_level(self, level: FormLevel) -> List[BodyComponent]:
        return [c for c in self.components.values() if c.form_level == level]

    @property
    def graph_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "components": {k: v.to_dict() for k, v in sorted(self.components.items())},
        }

    @classmethod
    def create_standard_humanoid_graph(cls, character_id: str = "Char_Standard") -> "SemanticBodyGraph":
        graph = cls(character_id=character_id)
        # Primary forms
        graph.add_component(BodyComponent("body.pelvis", FormLevel.PRIMARY, None, "MAT_BODY"))
        graph.add_component(BodyComponent("body.torso", FormLevel.PRIMARY, "body.pelvis", "MAT_BODY"))
        graph.add_component(BodyComponent("body.head", FormLevel.PRIMARY, "body.torso", "MAT_HEAD"))
        graph.add_component(BodyComponent("body.arm_L", FormLevel.PRIMARY, "body.torso", "MAT_LIMBS"))
        graph.add_component(BodyComponent("body.arm_R", FormLevel.PRIMARY, "body.torso", "MAT_LIMBS"))
        graph.add_component(BodyComponent("body.leg_L", FormLevel.PRIMARY, "body.pelvis", "MAT_LIMBS"))
        graph.add_component(BodyComponent("body.leg_R", FormLevel.PRIMARY, "body.pelvis", "MAT_LIMBS"))
        return graph
