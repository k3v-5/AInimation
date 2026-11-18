"""
ComponentizedCharacter assembly model supporting independent sub-components and partial rebuilds.
UAF-81.3 Sections 75, 87, 88, 93, 101.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.geometry_component import GeometryComponent
from ..models.mesh_data import MeshData
from ..anatomy.landmarks import LandmarkSystem
from ..anatomy.socket import AttachmentSocket
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ComponentizedCharacter:
    """
    Decoupled character hierarchy where Body, Head, Face, Hair, Clothing,
    and Armor are independent components rather than a single monolithic remeshed mesh.
    """
    character_id: str
    root: GeometryComponent
    landmarks: LandmarkSystem = field(default_factory=LandmarkSystem.create_default_humanoid)
    sockets: Dict[str, AttachmentSocket] = field(default_factory=dict)
    dirty_components: List[str] = field(default_factory=list)

    def get_component(self, component_id: str) -> Optional[GeometryComponent]:
        return self.root.find_component(component_id)

    def mark_dirty(self, component_id: str) -> None:
        if component_id not in self.dirty_components:
            self.dirty_components.append(component_id)

    def update_component(self, component_id: str, new_mesh: MeshData) -> bool:
        """
        Partial rebuild: Updates a single component's mesh without rebuilding the rest of the character.
        UAF-81.3 Section 75, 101.
        """
        comp = self.get_component(component_id)
        if not comp:
            return False
        comp.mesh_data = new_mesh
        if component_id in self.dirty_components:
            self.dirty_components.remove(component_id)
        return True

    @property
    def total_triangle_count(self) -> int:
        return self.root.total_triangle_count

    @property
    def assembly_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "root": self.root.to_dict(),
            "landmarks": self.landmarks.to_dict(),
            "sockets": {k: v.to_dict() for k, v in self.sockets.items()},
            "dirty_components": self.dirty_components,
            "total_triangle_count": self.total_triangle_count,
        }
