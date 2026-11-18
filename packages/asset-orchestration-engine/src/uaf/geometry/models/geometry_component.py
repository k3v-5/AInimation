"""
GeometryComponent represents a discrete semantic structural node in an asset assembly.
UAF-81.3 Sections 12, 13, 14, 68, 88.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .transform import Transform3D
from .mesh_data import MeshData
from .bounding_volume import AABB


@dataclass
class GeometryComponent:
    component_id: str
    semantic_role: str  # HEAD, TORSO, LIMB, ARMOR, CLOTHING, WEAPON, ACCESSORY, STRUCTURAL, DECORATIVE, FUNCTIONAL
    transform: Transform3D = field(default_factory=Transform3D)
    mesh_data: Optional[MeshData] = None
    children: List["GeometryComponent"] = field(default_factory=list)
    material_slots: List[str] = field(default_factory=list)
    visibility: bool = True
    quality_level: str = "production"
    lod_policy: str = "auto"
    collision_policy: str = "convex"

    def add_child(self, child: "GeometryComponent") -> None:
        child.transform.parent_id = self.component_id
        self.children.append(child)

    def find_component(self, component_id: str) -> Optional["GeometryComponent"]:
        if self.component_id == component_id:
            return self
        for child in self.children:
            found = child.find_component(component_id)
            if found:
                return found
        return None

    @property
    def total_triangle_count(self) -> int:
        count = self.mesh_data.triangle_count if self.mesh_data else 0
        for child in self.children:
            count += child.total_triangle_count
        return count

    def calculate_combined_aabb(self) -> AABB:
        all_points: List[List[float]] = []
        if self.mesh_data and self.mesh_data.vertices:
            # Simple translation offset from transform
            px, py, pz = self.transform.position
            for v in self.mesh_data.vertices:
                all_points.append([v[0] + px, v[1] + py, v[2] + pz])

        for child in self.children:
            child_aabb = child.calculate_combined_aabb()
            all_points.append(child_aabb.min_point)
            all_points.append(child_aabb.max_point)

        return AABB.from_points(all_points)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "semantic_role": self.semantic_role,
            "transform": self.transform.to_dict(),
            "mesh_data": self.mesh_data.to_dict() if self.mesh_data else None,
            "children": [c.to_dict() for c in self.children],
            "material_slots": self.material_slots,
            "visibility": self.visibility,
            "quality_level": self.quality_level,
            "lod_policy": self.lod_policy,
            "collision_policy": self.collision_policy,
            "total_triangle_count": self.total_triangle_count,
        }
