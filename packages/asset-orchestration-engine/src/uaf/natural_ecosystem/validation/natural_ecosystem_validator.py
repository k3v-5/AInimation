"""
NaturalEcosystemValidator enforces natural scale parameters, erosion limits, ecosystem components, and path purity.
UAF-81.51 Sections 134, 145, 146, 147.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import NaturalEcosystemSpecification


@dataclass
class NaturalEcosystemQualityScore:
    dimensions_erosion_score: float  # 0.0 to 1.0 (width, length > 0, height_scale >= 10m, erosion enabled)
    flora_rock_score: float          # 0.0 to 1.0 (vegetation and rocks enabled)
    water_navigation_score: float    # 0.0 to 1.0 (water, POI, navigation, and streaming enabled)
    unreal_score: float              # 0.0 to 1.0 (valid landscape, foliage, water, and nav paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_erosion_score +
            0.25 * self.flora_rock_score +
            0.25 * self.water_navigation_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_erosion_score": self.dimensions_erosion_score,
            "flora_rock_score": self.flora_rock_score,
            "water_navigation_score": self.water_navigation_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class NaturalEcosystemValidationReport:
    is_valid: bool
    quality_score: NaturalEcosystemQualityScore
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


class NaturalEcosystemValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 134, 145, 146, 147).
    """

    @classmethod
    def validate_natural_ecosystem(
        cls,
        spec: NaturalEcosystemSpecification,
        landscape_asset_path: str,
        foliage_asset_path: str,
        water_mesh_path: str,
        navmesh_path: str,
    ) -> NaturalEcosystemValidationReport:
        issues = []
        warnings = []

        # 1. Dimensions and erosion (Section 5, 16, 134)
        dim_ero_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_TERRAIN_DIMENSIONS: width={spec.dimensions.width_m}, "
                f"length={spec.dimensions.length_m}, height_scale={spec.dimensions.height_scale_m} (must be positive, scale >= 10.0m)."
            )
            dim_ero_score = 0.0
        if not spec.has_erosion:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Geomorphological erosion is disabled.")
            dim_ero_score = 0.0

        # 2. Flora and rocks (Section 26, 32, 119, 121, 134)
        flora_rock_score = 1.0
        if not spec.has_vegetation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Foliage/vegetation distribution is disabled.")
            flora_rock_score = 0.0
        if not spec.has_rocks:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Rock/boulder clustering is disabled.")
            flora_rock_score = 0.0

        # 3. Water and navigation/streaming (Section 36, 45, 124, 127, 130)
        water_nav_score = 1.0
        if not spec.has_water:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Hydrological/water system is disabled.")
            water_nav_score = 0.0
        if not spec.has_poi:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Natural POI landmark placement is disabled.")
            water_nav_score = 0.0
        if not spec.has_navigation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: AI navigation mesh is disabled.")
            water_nav_score = 0.0
        if not spec.has_streaming:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World partition streaming is disabled.")
            water_nav_score = 0.0

        # 4. Path purity check (Section 140)
        unreal_score = 1.0
        for p in [landscape_asset_path, foliage_asset_path, water_mesh_path, navmesh_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = NaturalEcosystemQualityScore(
            dimensions_erosion_score=dim_ero_score,
            flora_rock_score=flora_rock_score,
            water_navigation_score=water_nav_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return NaturalEcosystemValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
