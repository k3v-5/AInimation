"""
WorldBiomeValidator enforces valid world bounding boxes, biome parameter constraints, and relative path contracts.
UAF-81.32 Sections 9, 10, 27, 33, 119, 122.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import BiomeWorldDefinition


@dataclass
class WorldBiomeQualityScore:
    bounds_score: float     # 0.0 to 1.0 (Bounds valid, span >= 100cm)
    terrain_score: float    # 0.0 to 1.0 (Valid terrain reference)
    biome_score: float      # 0.0 to 1.0 (Biomes defined, temperature/humidity in [0.0, 1.0])
    streaming_score: float  # 0.0 to 1.0 (Valid level reference)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.bounds_score +
            0.20 * self.terrain_score +
            0.30 * self.biome_score +
            0.20 * self.streaming_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bounds_score": self.bounds_score,
            "terrain_score": self.terrain_score,
            "biome_score": self.biome_score,
            "streaming_score": self.streaming_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldBiomeValidationReport:
    is_valid: bool
    quality_score: WorldBiomeQualityScore
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


class WorldBiomeValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 9, 10, 27, 33, 119).
    """

    @classmethod
    def validate_world_biome(
        cls,
        world_def: BiomeWorldDefinition,
        terrain_ref: str,
        level_ref: str,
    ) -> WorldBiomeValidationReport:
        issues = []
        warnings = []

        # 1. World bounds check (Section 9 & 10)
        bounds_score = 1.0
        if not world_def.bounds.is_valid:
            issues.append(f"NON-NEGOTIABLE VIOLATION: World bounds are invalid: min must be < max with span >= 100cm: {world_def.bounds}.")
            bounds_score = 0.0

        # 2. Biomes validation (Section 28 & 33)
        biome_score = 1.0
        if not world_def.biomes:
            issues.append("NON-NEGOTIABLE VIOLATION: World contains zero configured biomes.")
            biome_score = 0.0

        for b in world_def.biomes:
            if not b.is_valid:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Biome '{b.biome_id}' has invalid parameter ranges (temperature/humidity must be in [0.0, 1.0]).")
                biome_score = 0.0

        # 3. Terrain reference check
        terrain_score = 1.0
        if not terrain_ref:
            issues.append("NON-NEGOTIABLE VIOLATION: World lacks heightmap terrain asset reference.")
            terrain_score = 0.0

        # 4. Path purity check (Section 119)
        stream_score = 1.0
        for ref in [terrain_ref, level_ref]:
            if ":\\" in ref or ":/" in ref or ref.startswith("/"):
                issues.append(f"NON-NEGOTIABLE VIOLATION: Absolute machine-dependent path detected: '{ref}'.")
                stream_score = 0.0

        q_score = WorldBiomeQualityScore(
            bounds_score=bounds_score,
            terrain_score=terrain_score,
            biome_score=biome_score,
            streaming_score=stream_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldBiomeValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
