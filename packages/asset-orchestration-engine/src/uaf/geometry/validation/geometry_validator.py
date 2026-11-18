"""
Comprehensive GeometryValidator checking transforms, topology, UVs, and visual artifacts.
UAF-81.3 Sections 64, 65, 66.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.geometry_component import GeometryComponent
from ..models.mesh_data import MeshData
from ..processing.topology import TopologyProcessor
from ..processing.uv import UVGenerator


@dataclass
class GeometryValidationReport:
    is_valid: bool
    component_id: str
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "component_id": self.component_id,
            "issues": self.issues,
            "warnings": self.warnings,
            "details": self.details,
        }


class GeometryValidator:
    """
    Multi-stage geometry validator ensuring mathematical, topological, and pipeline validity.
    """
    @classmethod
    def validate_component(
        cls,
        component: GeometryComponent,
        max_triangle_budget: Optional[int] = None,
        require_uvs: bool = True,
    ) -> GeometryValidationReport:
        issues = []
        warnings = []
        details = {}

        # 1. Transform validation
        scale = component.transform.scale
        if any(s <= 0 for s in scale):
            issues.append(f"Invalid non-positive scale: {scale}")

        # 2. Mesh data validation if present
        if component.mesh_data:
            mesh = component.mesh_data

            # Bounding volume check
            aabb = mesh.calculate_aabb()
            if any(dim <= 0 for dim in aabb.dimensions):
                warnings.append("Collapsed geometry: bounding box has zero thickness along one or more axes.")

            # Topology validation
            topo_rep = TopologyProcessor.analyze(mesh, max_triangle_budget=max_triangle_budget)
            details["topology"] = topo_rep.to_dict()
            if not topo_rep.is_valid:
                for err in topo_rep.issues:
                    issues.append(f"Topology error: {err}")

            # Normal validation
            if not mesh.normals:
                warnings.append("Mesh is missing explicit normals.")
            elif len(mesh.normals) != len(mesh.faces):
                warnings.append(f"Normal count ({len(mesh.normals)}) mismatch with face count ({len(mesh.faces)}).")

            # UV validation
            if require_uvs:
                uv_rep = UVGenerator.validate_uvs(mesh)
                details["uv"] = uv_rep.to_dict()
                if not uv_rep.is_valid:
                    for err in uv_rep.issues:
                        issues.append(f"UV error: {err}")

        # 3. Recursive children validation
        for child in component.children:
            child_rep = cls.validate_component(child, max_triangle_budget=max_triangle_budget, require_uvs=require_uvs)
            if not child_rep.is_valid:
                issues.extend([f"Child '{child.component_id}': {iss}" for iss in child_rep.issues])
            warnings.extend([f"Child '{child.component_id}': {w}" for w in child_rep.warnings])

        is_valid = len(issues) == 0
        return GeometryValidationReport(
            is_valid=is_valid,
            component_id=component.component_id,
            issues=issues,
            warnings=warnings,
            details=details,
        )
