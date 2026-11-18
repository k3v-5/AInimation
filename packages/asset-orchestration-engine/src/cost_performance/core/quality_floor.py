from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class QualityFloor:
    minimum_visual_score: float = 0.88
    minimum_geometry_score: float = 0.88
    minimum_material_score: float = 0.85
    minimum_uv_score: float = 0.85
    minimum_lod_score: float = 0.80
    minimum_collision_score: float = 0.85
    minimum_engine_readiness_score: float = 0.90
    maximum_allowed_regression: float = 0.00
    overall_quality_floor: float = 0.90

    def evaluate(self, candidate_scores: Dict[str, float]) -> Tuple[bool, str]:
        overall = candidate_scores.get("overall_quality", 0.0)
        if overall < self.overall_quality_floor:
            return False, f"Overall quality {overall:.4f} is below floor {self.overall_quality_floor:.4f}"

        visual = candidate_scores.get("visual", 1.0)
        if visual < self.minimum_visual_score:
            return False, f"Visual score {visual:.4f} is below floor {self.minimum_visual_score:.4f}"

        geo = candidate_scores.get("geometry", 1.0)
        if geo < self.minimum_geometry_score:
            return False, f"Geometry score {geo:.4f} is below floor {self.minimum_geometry_score:.4f}"

        readiness = candidate_scores.get("engine_readiness", 1.0)
        if readiness < self.minimum_engine_readiness_score:
            return False, f"Engine readiness score {readiness:.4f} is below floor {self.minimum_engine_readiness_score:.4f}"

        regression = candidate_scores.get("regression_delta", 0.0)
        if regression < -self.maximum_allowed_regression:
            return False, f"Regression delta {regression:.4f} exceeds allowed {self.maximum_allowed_regression:.4f}"

        return True, "Passed Quality Floor requirements"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimum_visual_score": self.minimum_visual_score,
            "minimum_geometry_score": self.minimum_geometry_score,
            "minimum_material_score": self.minimum_material_score,
            "minimum_uv_score": self.minimum_uv_score,
            "minimum_lod_score": self.minimum_lod_score,
            "minimum_collision_score": self.minimum_collision_score,
            "minimum_engine_readiness_score": self.minimum_engine_readiness_score,
            "maximum_allowed_regression": self.maximum_allowed_regression,
            "overall_quality_floor": self.overall_quality_floor
        }
