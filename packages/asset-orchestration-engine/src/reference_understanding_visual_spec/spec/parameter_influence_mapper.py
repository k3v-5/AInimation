from typing import Dict, Any, List, Optional
from ..core.reference_schema import FeatureParameterAttribution

class ParameterInfluenceMapper:
    DEFAULT_MAP: Dict[str, FeatureParameterAttribution] = {
        "roof_silhouette": FeatureParameterAttribution(
            feature_name="roof_silhouette",
            candidate_parameters=["roof_height", "roof_width", "roof_pitch"],
            sensitivity_rating="HIGH",
            confidence=0.96
        ),
        "facade_proportions": FeatureParameterAttribution(
            feature_name="facade_proportions",
            candidate_parameters=["width", "wall_height"],
            sensitivity_rating="HIGH",
            confidence=0.95
        ),
        "eaves_overhang": FeatureParameterAttribution(
            feature_name="eaves_overhang",
            candidate_parameters=["roof_overhang", "roof_width"],
            sensitivity_rating="MEDIUM",
            confidence=0.90
        ),
        "fenestration": FeatureParameterAttribution(
            feature_name="fenestration",
            candidate_parameters=["window_count", "window_sill_height"],
            sensitivity_rating="MEDIUM",
            confidence=0.88
        )
    }

    @classmethod
    def get_attribution(cls, feature_name: str) -> Optional[FeatureParameterAttribution]:
        return cls.DEFAULT_MAP.get(feature_name)
