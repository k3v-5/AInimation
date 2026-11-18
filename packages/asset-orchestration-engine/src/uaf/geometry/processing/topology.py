"""
Topology analysis and polygon/triangle budget evaluation.
UAF-81.3 Sections 47, 48, 49, 50.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..models.mesh_data import MeshData


@dataclass
class TopologyReport:
    is_valid: bool
    triangle_count: int
    vertex_count: int
    is_manifold: bool
    has_degenerate_faces: bool
    budget_exceeded: bool = False
    max_budget: Optional[int] = None
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "triangle_count": self.triangle_count,
            "vertex_count": self.vertex_count,
            "is_manifold": self.is_manifold,
            "has_degenerate_faces": self.has_degenerate_faces,
            "budget_exceeded": self.budget_exceeded,
            "max_budget": self.max_budget,
            "issues": self.issues,
        }


class TopologyProcessor:
    """
    Evaluates mesh topology quality, manifoldness, and triangle budget compliance.
    """
    @classmethod
    def analyze(cls, mesh: MeshData, max_triangle_budget: Optional[int] = None) -> TopologyReport:
        triangles = mesh.triangle_count
        vertices = mesh.vertex_count
        manifold = mesh.is_manifold()
        degenerate = mesh.has_degenerate_faces()

        issues = []
        if not manifold:
            issues.append("Non-manifold geometry detected (edges shared by >2 faces).")
        if degenerate:
            issues.append("Degenerate faces detected (duplicate indices).")

        budget_exceeded = False
        if max_triangle_budget is not None and triangles > max_triangle_budget:
            budget_exceeded = True
            issues.append(f"Triangle count {triangles} exceeds max budget {max_triangle_budget}.")

        is_valid = len(issues) == 0

        return TopologyReport(
            is_valid=is_valid,
            triangle_count=triangles,
            vertex_count=vertices,
            is_manifold=manifold,
            has_degenerate_faces=degenerate,
            budget_exceeded=budget_exceeded,
            max_budget=max_triangle_budget,
            issues=issues,
        )
