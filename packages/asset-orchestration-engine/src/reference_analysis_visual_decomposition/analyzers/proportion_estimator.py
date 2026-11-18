from typing import Dict, Any
from ..core.reference_schema import ProportionEstimate

class ProportionEstimator:
    @classmethod
    def estimate_proportions(cls, image_metadata: Dict[str, Any]) -> ProportionEstimate:
        h_w = float(image_metadata.get("aspect_ratio", 1.42))
        ratios = image_metadata.get("component_ratios", {"body": 0.80, "top_ring": 0.10, "bottom_ring": 0.10})
        curvature = float(image_metadata.get("curvature", 0.25))

        return ProportionEstimate(
            height_to_width_ratio=round(h_w, 2),
            component_ratios=ratios,
            estimated_curvature=curvature,
            tolerance=0.05
        )
