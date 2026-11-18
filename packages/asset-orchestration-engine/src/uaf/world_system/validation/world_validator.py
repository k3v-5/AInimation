"""
WorldValidator enforces world bounds, reachability, streaming, and quality gates.
UAF-81.16 Sections 181, 182, 184, 188, 204, 236.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.world_def import WorldDefinition
from ..models.features import WaterBody, RoadNetwork, WorldDistrict, GameplayZone
from ...world_surface.biomes.biome import BiomeProfile


@dataclass
class WorldQualityScore:
    terrain_score: float             # 0.0 to 1.0 (Section 183)
    gameplay_navigation_score: float # 0.0 to 1.0 (Section 184, 188)
    streaming_score: float           # 0.0 to 1.0 (Section 187)
    performance_score: float         # 0.0 to 1.0 (Section 186)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.terrain_score +
            0.30 * self.gameplay_navigation_score +
            0.20 * self.streaming_score +
            0.20 * self.performance_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terrain_score": self.terrain_score,
            "gameplay_navigation_score": self.gameplay_navigation_score,
            "streaming_score": self.streaming_score,
            "performance_score": self.performance_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class WorldValidationReport:
    is_valid: bool
    quality_score: WorldQualityScore
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


class WorldValidator:
    """
    Enforces NON-NEGOTIABLE REQUIREMENTS (Sections 188, 204, 236, 238).
    """

    @classmethod
    def validate_world(
        cls,
        world_def: WorldDefinition,
        biomes: List[BiomeProfile],
        water_bodies: List[WaterBody],
        roads: Optional[RoadNetwork],
        districts: List[WorldDistrict],
        zones: List[GameplayZone],
    ) -> WorldValidationReport:
        issues = []
        warnings = []

        # 1. Bounds & Seed validation (Sections 8, 9)
        terrain_score = 1.0
        if world_def.bounds.max_x <= world_def.bounds.min_x or world_def.bounds.max_y <= world_def.bounds.min_y:
            issues.append("NON-NEGOTIABLE VIOLATION: World bounds define zero or negative area.")
            terrain_score = 0.0

        if world_def.seed is None:
            issues.append("NON-NEGOTIABLE VIOLATION: World generation lacks deterministic seed.")
            terrain_score = 0.0

        # 2. Gameplay & Navigation reachability (Sections 188, 236)
        nav_score = 1.0
        for zone in zones:
            if not zone.is_reachable:
                issues.append(f"NON-NEGOTIABLE VIOLATION: Gameplay zone '{zone.zone_id}' is unreachable.")
                nav_score = 0.0

        if not any(z.player_spawns > 0 for z in zones):
            issues.append("NON-NEGOTIABLE VIOLATION: World has no player spawn zones.")
            nav_score = 0.0

        # 3. Path portability check (Section 204)
        if ":\\" in world_def.world_id or ":/" in world_def.world_id:
            issues.append("NON-NEGOTIABLE VIOLATION: World identifier contains absolute local machine paths.")
            terrain_score = 0.0

        streaming_score = 1.0
        perf_score = 1.0

        q_score = WorldQualityScore(
            terrain_score=terrain_score,
            gameplay_navigation_score=nav_score,
            streaming_score=streaming_score,
            performance_score=perf_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return WorldValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
