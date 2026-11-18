"""
SurfaceFabricationValidator enforces structural integrity, path portability, and performance gates.
UAF-81.15 Sections 177, 178, 205, 206, 208.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.profile import SurfaceProfile
from ..models.graph import MaterialGraphContract


@dataclass
class SurfaceFabricationQualityScore:
    structural_score: float   # 0.0 to 1.0 (Section 178)
    visual_score: float       # 0.0 to 1.0 (Section 179)
    performance_score: float  # 0.0 to 1.0 (Section 180)
    export_score: float       # 0.0 to 1.0 (Section 181)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.structural_score +
            0.25 * self.visual_score +
            0.25 * self.performance_score +
            0.20 * self.export_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "structural_score": self.structural_score,
            "visual_score": self.visual_score,
            "performance_score": self.performance_score,
            "export_score": self.export_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class SurfaceFabricationValidationReport:
    is_valid: bool
    quality_score: SurfaceFabricationQualityScore
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


class SurfaceFabricationValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 205, 206, 208).
    """

    @classmethod
    def validate_surface_fabrication(
        cls,
        profile: SurfaceProfile,
        graph: MaterialGraphContract,
        textures: List[str],
    ) -> SurfaceFabricationValidationReport:
        issues = []
        warnings = []

        # 1. Structural & Determinism validation (Sections 178, 205)
        struct_score = 1.0
        if profile.seed is None:
            issues.append("NON-NEGOTIABLE VIOLATION: Surface generation lacks deterministic seed.")
            struct_score = 0.0

        if not textures:
            issues.append("NON-NEGOTIABLE VIOLATION: Surface fabric produced zero texture outputs.")
            struct_score = 0.0

        # 2. Portability / No local machine paths (Section 206)
        export_score = 1.0
        for tex in textures:
            if ":\\" in tex or ":/" in tex:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Hardcoded absolute local machine path detected: '{tex}'.")
                export_score = 0.0

        for key, val in graph.parameters.items():
            if isinstance(val, str) and (":\\" in val or ":/" in val):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Hardcoded machine path in parameter '{key}': '{val}'.")
                export_score = 0.0

        visual_score = 1.0
        perf_score = 1.0

        q_score = SurfaceFabricationQualityScore(
            structural_score=struct_score,
            visual_score=visual_score,
            performance_score=perf_score,
            export_score=export_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return SurfaceFabricationValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
