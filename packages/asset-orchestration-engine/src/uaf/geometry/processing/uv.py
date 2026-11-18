"""
UV generation and texel density calculation.
UAF-81.3 Sections 55, 56, 57, 58.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.mesh_data import MeshData


@dataclass
class UVReport:
    is_valid: bool
    has_uvs: bool
    out_of_bounds_count: int = 0
    texel_density: float = 0.0  # px / meter
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "has_uvs": self.has_uvs,
            "out_of_bounds_count": self.out_of_bounds_count,
            "texel_density": self.texel_density,
            "issues": self.issues,
        }


class UVGenerator:
    """
    Generates and validates texture UV coordinates.
    """
    @classmethod
    def generate_planar_uvs(cls, mesh: MeshData) -> None:
        """Projects XZ or XY coordinates into UV [0, 1] range."""
        if not mesh.vertices:
            return

        min_x = min(v[0] for v in mesh.vertices)
        max_x = max(v[0] for v in mesh.vertices)
        min_y = min(v[1] for v in mesh.vertices)
        max_y = max(v[1] for v in mesh.vertices)

        range_x = max(1e-6, max_x - min_x)
        range_y = max(1e-6, max_y - min_y)

        mesh.uvs = []
        for v in mesh.vertices:
            u = round((v[0] - min_x) / range_x, 5)
            w = round((v[1] - min_y) / range_y, 5)
            mesh.uvs.append([u, w])

    @classmethod
    def validate_uvs(cls, mesh: MeshData, texture_resolution: int = 2048) -> UVReport:
        if not mesh.uvs:
            return UVReport(is_valid=False, has_uvs=False, issues=["Mesh has no UV coordinates."])

        out_of_bounds = 0
        for uv in mesh.uvs:
            if uv[0] < -0.01 or uv[0] > 1.01 or uv[1] < -0.01 or uv[1] > 1.01:
                out_of_bounds += 1

        aabb = mesh.calculate_aabb()
        surface_size = max(0.01, max(aabb.dimensions))
        # Simple texel density estimation: resolution / surface size in meters
        texel_density = round(texture_resolution / surface_size, 2)

        issues = []
        if out_of_bounds > 0:
            issues.append(f"{out_of_bounds} UV vertices are out of [0, 1] bounds.")

        return UVReport(
            is_valid=len(issues) == 0,
            has_uvs=True,
            out_of_bounds_count=out_of_bounds,
            texel_density=texel_density,
            issues=issues,
        )
