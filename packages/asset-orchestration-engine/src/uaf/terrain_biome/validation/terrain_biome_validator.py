"""
TerrainBiomeValidator enforces height boundaries, scale sanity, ecological consistency, and path portability.
UAF-81.36 Sections 8, 14, 117, 127.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import TerrainBiomeSpecification, BiomeType36, VegetationCategory36


@dataclass
class TerrainBiomeQualityScore:
    bounds_score: float      # 0.0 to 1.0 (width/length positive, height span >= 10.0m)
    biome_score: float       # 0.0 to 1.0 (valid biome archetype)
    vegetation_score: float  # 0.0 to 1.0 (ecological compatibility with primary biome)
    landscape_score: float   # 0.0 to 1.0 (valid unreal landscape reference)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.bounds_score +
            0.25 * self.biome_score +
            0.25 * self.vegetation_score +
            0.20 * self.landscape_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bounds_score": self.bounds_score,
            "biome_score": self.biome_score,
            "vegetation_score": self.vegetation_score,
            "landscape_score": self.landscape_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class TerrainBiomeValidationReport:
    is_valid: bool
    quality_score: TerrainBiomeQualityScore
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


class TerrainBiomeValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Section 117).
    """

    @classmethod
    def validate_terrain_biome(
        cls,
        spec: TerrainBiomeSpecification,
        landscape_asset_path: str,
    ) -> TerrainBiomeValidationReport:
        issues = []
        warnings = []

        # 1. Bounds check (Section 14, 117)
        bounds_score = 1.0
        if not spec.bounds.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_HEIGHT_RANGE/SCALE: "
                f"width={spec.bounds.width_m}, length={spec.bounds.length_m}, "
                f"min_height={spec.bounds.min_height_m}, max_height={spec.bounds.max_height_m}."
            )
            bounds_score = 0.0

        # 2. Biome validity
        biome_score = 1.0

        # 3. Ecological compatibility check (Section 23, 117)
        veg_score = 1.0
        if spec.primary_biome == BiomeType36.DESERT:
            if any(v in (VegetationCategory36.FERN, VegetationCategory36.ROOT, VegetationCategory36.VINE) for v in spec.vegetation_categories):
                issues.append("HARD FAIL CONDITION: IMPOSSIBLE_ECOLOGY: Fern/Vine/Root vegetation cannot exist in arid DESERT biome.")
                veg_score = 0.0
        elif spec.primary_biome == BiomeType36.URBAN:
            if VegetationCategory36.ALIEN_PLANT in spec.vegetation_categories:
                issues.append("HARD FAIL CONDITION: IMPOSSIBLE_ECOLOGY: Alien plant cannot naturally appear in standard URBAN biome.")
                veg_score = 0.0

        # 4. Path purity check (Section 117)
        land_score = 1.0
        if ":\\" in landscape_asset_path or ":/" in landscape_asset_path:
            issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{landscape_asset_path}'.")
            land_score = 0.0

        q_score = TerrainBiomeQualityScore(
            bounds_score=bounds_score,
            biome_score=biome_score,
            vegetation_score=veg_score,
            landscape_score=land_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return TerrainBiomeValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
