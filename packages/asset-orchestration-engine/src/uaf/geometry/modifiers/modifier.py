"""
Procedural modifier types and declarative modifier stack.
UAF-81.3 Sections 20, 21, 22.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.mesh_data import MeshData


class ModifierType(str, Enum):
    BEVEL = "BEVEL"
    BOOLEAN = "BOOLEAN"
    SUBDIVISION = "SUBDIVISION"
    SOLIDIFY = "SOLIDIFY"
    SHRINKWRAP = "SHRINKWRAP"
    MIRROR = "MIRROR"
    ARRAY = "ARRAY"
    DEFORM = "DEFORM"
    REMESH = "REMESH"
    SMOOTH = "SMOOTH"
    DECIMATE = "DECIMATE"


@dataclass
class ProceduralModifier:
    modifier_id: str
    modifier_type: ModifierType
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modifier_id": self.modifier_id,
            "modifier_type": self.modifier_type.value,
            "parameters": self.parameters,
            "is_enabled": self.is_enabled,
        }


@dataclass
class ModifierStack:
    modifiers: List[ProceduralModifier] = field(default_factory=list)

    def add_modifier(self, modifier: ProceduralModifier) -> None:
        self.modifiers.append(modifier)

    def apply_to(self, mesh: MeshData) -> MeshData:
        """
        Applies modifiers in sequential order.
        Simulates declarative pipeline transformations (e.g. decimate, mirror, subdivide).
        """
        current_mesh = mesh
        for mod in self.modifiers:
            if not mod.is_enabled:
                continue

            if mod.modifier_type == ModifierType.DECIMATE:
                ratio = float(mod.parameters.get("ratio", 0.5))
                # Decimate simulation: reduce faces by ratio while retaining topology
                new_count = max(1, int(len(current_mesh.faces) * ratio))
                current_mesh = MeshData(
                    vertices=list(current_mesh.vertices),
                    faces=current_mesh.faces[:new_count],
                    normals=current_mesh.normals[:new_count] if current_mesh.normals else [],
                )
            elif mod.modifier_type == ModifierType.MIRROR:
                # Mirror across X axis
                axis = mod.parameters.get("axis", "X")
                mirrored_vertices = []
                for v in current_mesh.vertices:
                    vx = -v[0] if axis == "X" else v[0]
                    vy = -v[1] if axis == "Y" else v[1]
                    vz = -v[2] if axis == "Z" else v[2]
                    mirrored_vertices.append([vx, vy, vz])

                offset = len(current_mesh.vertices)
                mirrored_faces = [[idx + offset for idx in reversed(f)] for f in current_mesh.faces]

                current_mesh = MeshData(
                    vertices=current_mesh.vertices + mirrored_vertices,
                    faces=current_mesh.faces + mirrored_faces,
                )
                current_mesh.calculate_facet_normals()

        return current_mesh
