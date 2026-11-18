"""
TerrainWorldValidator enforces geographic bounds, heightspan, core ecosystem subsystems, and path purity.
UAF-81.48 Sections 25, 124, 137, 138, 139.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.definition import TerrainWorldSpecification


@dataclass
class TerrainWorldQualityScore:
    dimensions_erosion_score: float    # 0.0 to 1.0 (width, length > 0, height_delta >= 10m, erosion enabled)
    biome_features_score: float        # 0.0 to 1.0 (roads, POIs, and vegetation enabled)
    navigation_streaming_score: float  # 0.0 to 1.0 (navigation and streaming enabled)
    unreal_score: float                # 0.0 to 1.0 (valid landscape, partition, and navmesh paths)

    @property
    def aggregate_score(self) -> float:
        return round(
            0.30 * self.dimensions_erosion_score +
            0.25 * self.biome_features_score +
            0.25 * self.navigation_streaming_score +
            0.20 * self.unreal_score,
            3
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions_erosion_score": self.dimensions_erosion_score,
            "biome_features_score": self.biome_features_score,
            "navigation_streaming_score": self.navigation_streaming_score,
            "unreal_score": self.unreal_score,
            "aggregate_score": self.aggregate_score,
        }


@dataclass
class TerrainWorldValidationReport:
    is_valid: bool
    quality_score: TerrainWorldQualityScore
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


class TerrainWorldValidator:
    """
    Enforces NON-NEGOTIABLE HARD FAIL CONDITIONS (Sections 25, 124, 137, 139).
    """

    @classmethod
    def validate_terrain_world(
        cls,
        spec: TerrainWorldSpecification,
        landscape_asset_path: str,
        world_partition_path: str,
        navmesh_path: str,
    ) -> TerrainWorldValidationReport:
        issues = []
        warnings = []

        # 1. Terrain dimensions and erosion validation (Section 10, 22, 25)
        dim_score = 1.0
        if not spec.dimensions.is_valid:
            issues.append(
                f"HARD FAIL CONDITION: INVALID_TERRAIN_DIMENSIONS: width={spec.dimensions.width_m}, "
                f"length={spec.dimensions.length_m}, height_delta={spec.dimensions.height_delta_m} must be positive with height delta >= 10.0m."
            )
            dim_score = 0.0
        if not spec.has_erosion:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Geomorphological erosion is disabled.")
            dim_score = 0.0

        # 2. Biome features: roads, POIs, vegetation (Section 1, 4, 120, 124)
        biome_score = 1.0
        if not spec.has_roads:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Road network generation is disabled.")
            biome_score = 0.0
        if not spec.has_poi:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Point-of-Interest (POI) settlement generation is disabled.")
            biome_score = 0.0
        if not spec.has_vegetation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: Biome vegetation distribution is disabled.")
            biome_score = 0.0

        # 3. Navigation and streaming (Section 49, 51, 121, 122)
        nav_stream_score = 1.0
        if not spec.has_navigation:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World AI navigation is disabled.")
            nav_stream_score = 0.0
        if not spec.has_streaming:
            issues.append("HARD FAIL CONDITION: MISSING_CORE_SUBSYSTEMS: World partition streaming is disabled.")
            nav_stream_score = 0.0

        # 4. Path purity check (Section 142)
        unreal_score = 1.0
        for p in [landscape_asset_path, world_partition_path, navmesh_path]:
            if ":\\" in p or ":/" in p:
                issues.append(f"HARD FAIL CONDITION: Absolute machine-dependent path detected: '{p}'.")
                unreal_score = 0.0

        q_score = TerrainWorldQualityScore(
            dimensions_erosion_score=dim_score,
            biome_features_score=biome_score,
            navigation_streaming_score=nav_stream_score,
            unreal_score=unreal_score,
        )

        is_valid = len(issues) == 0 and q_score.aggregate_score >= 0.85
        review_status = "PASSED" if is_valid else "MANUAL_REVIEW_REQUIRED"

        return TerrainWorldValidationReport(
            is_valid=is_valid,
            quality_score=q_score,
            issues=issues,
            warnings=warnings,
            review_status=review_status,
        )
