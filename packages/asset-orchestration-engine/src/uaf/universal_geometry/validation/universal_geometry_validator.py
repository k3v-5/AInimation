"""
UniversalGeometryValidator enforces dimensional non-negativity, topological integrity, normal/UV presence, and path purity.
UAF-81.53 Sections 142, 162, 165.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import UniversalMeshSpecification


@dataclass
class UniversalGeometryQualityScore:
    bounds_topology_score: float  # 0.0 to 1.0 (positive dimensions, vertex >= 3, tri >= 1)
    normal_uv_score: float        # 0.0 to 1.0 (normals, tangents, and UVs enabled)
    lod_collision_score: float    # 0.0 to 1.0 (collision and LODs enabled)
    unreal_score: float           # 0.0 to 1.0 (valid static mesh, collision, and LOD paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.bounds_topology_score +
            0.25 * self.normal_uv_score +
            0.25 * self.lod_collision_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bounds_topology_score": self.bounds_topology_score,
            "normal_uv_score": self.normal_uv_score,
            "lod_collision_score": self.lod_collision_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class UniversalGeometryValidationReport:
    is_valid: bool
    quality_score: UniversalGeometryQualityScore
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_status: str = "PASSED"  # "PASSED", "MANUAL_REVIEW_REQUIRED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": self.quality_score.to_dict(),
            "issues": self.issues,
            "warnings": self.warnings,
            "review_status": self.review_status,
        }


class UniversalGeometryValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 142, 162, 165).
    """

    @classmethod
    def validate_universal_geometry(
        cls,
        spec: UniversalMeshSpecification,
        static_mesh_path: str,
        collision_mesh_path: str,
        lod_mesh_path: str,
    ) -> UniversalGeometryValidationReport:
        issues = []
        warnings = []

        # 1. Bounds and topology counts (Section 4, 142, 162)
        bounds_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_MESH_DIMENSIONS: width={spec.dimensions.width_cm}, "
                f"length={spec.dimensions.length_cm}, height={spec.dimensions.height_cm} must be positive."
            )
            bounds_score = 0.0
        if spec.vertex_count < 3 or spec.triangle_count < 1:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_TOPOLOGY_COUNTS: vertex_count={spec.vertex_count} (>=3), "
                f"triangle_count={spec.triangle_count} (>=1)."
            )
            bounds_score = 0.0

        # 2. Normals, tangents, UVs (Section 147, 148, 149)
        norm_uv_score = 1.0
        if not (spec.has_normals and spec.has_tangents and spec.has_uv):
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Normals, tangents, and UVs are mandatory.")
            norm_uv_score = 0.0

        # 3. Collision and LODs (Section 154, 155)
        lod_col_score = 1.0
        if not spec.has_collision:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Collision representation is disabled.")
            lod_col_score = 0.0
        if not spec.has_lod:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: LOD chain generation is disabled.")
            lod_col_score = 0.0

        # 4. Path purity check (Section 165)
        unreal_score = 1.0
        for p in [static_mesh_path, collision_mesh_path, lod_mesh_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = UniversalGeometryQualityScore(
            bounds_topology_score=bounds_score,
            normal_uv_score=norm_uv_score,
            lod_collision_score=lod_col_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return UniversalGeometryValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
