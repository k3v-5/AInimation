from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ProblemFeatures:
    asset_category: str = "WEAPON"
    asset_complexity: str = "HIGH"
    part_count: int = 7
    geometry_complexity: str = "HIGH"
    material_complexity: str = "PBR_DUAL"
    reference_count: int = 1
    reference_quality: float = 0.95
    reference_similarity: float = 0.90
    required_detail_level: str = "HERO_FIRST_PERSON"
    target_platform: str = "PC_CONSOLE"
    target_engine: str = "UNREAL_ENGINE_5"
    polygon_budget: int = 15000
    material_budget: int = 2
    texture_budget: int = 2
    lod_requirement: int = 3
    collision_requirement: str = "UCX_CONVEX"
    animation_requirement: bool = False
    visual_fidelity_requirement: float = 0.90
    time_budget: float = 60.0
    resource_budget: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_category": self.asset_category,
            "asset_complexity": self.asset_complexity,
            "part_count": self.part_count,
            "geometry_complexity": self.geometry_complexity,
            "material_complexity": self.material_complexity,
            "reference_count": self.reference_count,
            "reference_quality": self.reference_quality,
            "reference_similarity": self.reference_similarity,
            "required_detail_level": self.required_detail_level,
            "target_platform": self.target_platform,
            "target_engine": self.target_engine,
            "polygon_budget": self.polygon_budget,
            "material_budget": self.material_budget,
            "texture_budget": self.texture_budget,
            "lod_requirement": self.lod_requirement,
            "collision_requirement": self.collision_requirement,
            "animation_requirement": self.animation_requirement,
            "visual_fidelity_requirement": self.visual_fidelity_requirement,
            "time_budget": self.time_budget,
            "resource_budget": self.resource_budget
        }

class FeatureExtractor:
    """Extracts standardized ProblemFeatures from raw asset requests or specs."""

    @staticmethod
    def extract(request_data: Dict[str, Any]) -> ProblemFeatures:
        return ProblemFeatures(
            asset_category=request_data.get("category", request_data.get("asset_category", "WEAPON")),
            asset_complexity=request_data.get("complexity", "HIGH"),
            part_count=request_data.get("part_count", 7),
            geometry_complexity=request_data.get("geometry_complexity", "HIGH"),
            material_complexity=request_data.get("material_complexity", "PBR_DUAL"),
            polygon_budget=request_data.get("polygon_budget", 15000),
            material_budget=request_data.get("material_budget", 2),
            lod_requirement=request_data.get("lod_requirement", 3),
            visual_fidelity_requirement=request_data.get("visual_fidelity_requirement", 0.90),
            time_budget=request_data.get("time_budget", 60.0)
        )
