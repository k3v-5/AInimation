"""
WorldSurfaceValidator enforces non-negotiable rules for terrain, biomes, and vegetation clearance.
UAF-81.13 Sections 172, 175, 202, 204, 208, 209.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..terrain.territory import TerritoryModel
from ..terrain.landmark import NaturalLandmark
from ..biomes.biome import BiomeProfile


@dataclass
class WorldSurfaceQualityScore:
    terrain_score: float              # 0.0 to 1.0
    biome_coherence_score: float      # 0.0 to 1.0
    vegetation_clearance_score: float # 0.0 to 1.0
    navigation_score: float           # 0.0 to 1.0
    gameplay_score: float             # 0.0 to 1.0

    @property
    def aggregate_score(self) -> float:
        return round(
            0.25 * self.terrain_score +
            0.25 * self.biome_coherence_score +
            0.20 * self.vegetation_clearance_score +
            0.15 * self.navigation_score +
            0.15 * self.gameplay_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terrain_score": self.terrain_score,
            "biome_coherence_score": self.biome_coherence_score,
            "vegetation_clearance_score": self.vegetation_clearance_score,
            "navigation_score": self.navigation_score,
            "gameplay_score": self.gameplay_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldSurfaceValidationReport:
    is_valid: bool
    quality_score: WorldSurfaceQualityScore
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


class WorldSurfaceValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 202, 204, 208, 209).
    """

    @classmethod
    def validate_world_surface(
        cls,
        territory: TerritoryModel,
        biomes: List[BiomeProfile],
        landmarks: Optional[List[NaturalLandmark]] = None,
        has_vegetation_blocking_spawn: bool = False,
    ) -> WorldSurfaceValidationReport:
        issues = []
        warnings = []

        # 1. Terrain & Seed validation (Section 202)
        terrain_score = 1.0
        if territory.world_width_m <= 0 or territory.world_length_m <= 0:
            issues.append("NON-NEGOTIABLE VIOLATION: Territory has non-positive area dimensions.")
            terrain_score = 0.0
        if territory.seed is None:
            issues.append("NON-NEGOTIABLE VIOLATION: Random terrain without deterministic seed.")
            terrain_score = 0.0

        # 2. Biome coherence & non-flat terrain (Section 208, 209)
        biome_score = 1.0
        if not biomes:
            issues.append("NON-NEGOTIABLE VIOLATION: World surface has no assigned biomes.")
            biome_score = 0.0
        if territory.max_height_m <= territory.min_height_m:
            issues.append("NON-NEGOTIABLE VIOLATION: Subsystem assumes flat terrain (max_height <= min_height).")
            biome_score = 0.0

        # 3. Vegetation clearance rule (Section 204)
        if has_vegetation_blocking_spawn:
            issues.append("NON-NEGOTIABLE VIOLATION: Foliage blocks player spawn point or critical path.")
            veg_clearance_score = 0.0
        else:
            veg_clearance_score = 1.0

        nav_score = 1.0
        gameplay_score = 1.0 if landmarks else 0.8
        if not landmarks:
            warnings.append("World surface lacks natural orienting landmarks.")

        q_score = WorldSurfaceQualityScore(
            terrain_score=terrain_score,
            biome_coherence_score=biome_score,
            vegetation_clearance_score=veg_clearance_score,
            navigation_score=nav_score,
            gameplay_score=gameplay_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.80
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldSurfaceValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
