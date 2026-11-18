from typing import Dict, Optional
from ..core.evaluation_types import EvaluationDimension
from ..models.evaluation_models import EvaluationProfile

def create_weapon_profile() -> EvaluationProfile:
    return EvaluationProfile(
        profile_id="PROFILE_WEAPON_DARX",
        name="DarX Weapon Evaluation Profile",
        version="1.0.0",
        dimension_weights={
            EvaluationDimension.VISUAL_MATCH: 1.5,
            EvaluationDimension.SILHOUETTE: 1.5,
            EvaluationDimension.PROPORTION: 1.2,
            EvaluationDimension.GEOMETRY: 1.2,
            EvaluationDimension.TOPOLOGY: 1.0,
            EvaluationDimension.MATERIAL: 1.2,
            EvaluationDimension.TEXTURE: 1.0,
            EvaluationDimension.UV: 1.0,
            EvaluationDimension.DETAIL: 1.0,
            EvaluationDimension.STYLE_CONSISTENCY: 1.2,
            EvaluationDimension.FUNCTIONAL_STRUCTURE: 1.0,
            EvaluationDimension.COLLISION: 1.0,
            EvaluationDimension.LOD: 1.0,
            EvaluationDimension.ENGINE_READINESS: 1.5,
            EvaluationDimension.PERFORMANCE: 1.0,
            EvaluationDimension.PACKAGE_INTEGRITY: 1.0,
            EvaluationDimension.SEMANTIC_COMPLIANCE: 1.2
        },
        minimum_global_score=0.85,
        minimum_dimension_scores={
            EvaluationDimension.SILHOUETTE: 0.80,
            EvaluationDimension.GEOMETRY: 0.85,
            EvaluationDimension.ENGINE_READINESS: 0.90,
            EvaluationDimension.MATERIAL: 0.75
        },
        critical_dimensions=[
            EvaluationDimension.GEOMETRY,
            EvaluationDimension.ENGINE_READINESS,
            EvaluationDimension.SILHOUETTE
        ],
        maximum_allowed_defects=5,
        maximum_critical_defects=0,
        minimum_confidence=0.80
    )

def create_unreal_ready_profile() -> EvaluationProfile:
    return EvaluationProfile(
        profile_id="PROFILE_UNREAL_READY",
        name="Unreal Ready Production Asset Profile",
        version="1.0.0",
        dimension_weights={
            EvaluationDimension.GEOMETRY: 1.5,
            EvaluationDimension.TOPOLOGY: 1.2,
            EvaluationDimension.COLLISION: 1.5,
            EvaluationDimension.LOD: 1.5,
            EvaluationDimension.ENGINE_READINESS: 2.0,
            EvaluationDimension.PACKAGE_INTEGRITY: 1.5,
            EvaluationDimension.PERFORMANCE: 1.2
        },
        minimum_global_score=0.90,
        minimum_dimension_scores={
            EvaluationDimension.ENGINE_READINESS: 0.95,
            EvaluationDimension.COLLISION: 0.90,
            EvaluationDimension.LOD: 0.85
        },
        critical_dimensions=[
            EvaluationDimension.ENGINE_READINESS,
            EvaluationDimension.COLLISION
        ],
        maximum_allowed_defects=3,
        maximum_critical_defects=0,
        minimum_confidence=0.85
    )

def create_visual_asset_profile() -> EvaluationProfile:
    return EvaluationProfile(
        profile_id="PROFILE_VISUAL_ART",
        name="Visual Art & Style Consistency Profile",
        version="1.0.0",
        dimension_weights={
            EvaluationDimension.VISUAL_MATCH: 2.0,
            EvaluationDimension.SILHOUETTE: 1.8,
            EvaluationDimension.PROPORTION: 1.5,
            EvaluationDimension.MATERIAL: 1.5,
            EvaluationDimension.STYLE_CONSISTENCY: 1.8,
            EvaluationDimension.DETAIL: 1.2
        },
        minimum_global_score=0.80,
        minimum_dimension_scores={
            EvaluationDimension.VISUAL_MATCH: 0.80,
            EvaluationDimension.SILHOUETTE: 0.80
        },
        critical_dimensions=[
            EvaluationDimension.VISUAL_MATCH,
            EvaluationDimension.SILHOUETTE
        ],
        maximum_allowed_defects=8,
        maximum_critical_defects=0,
        minimum_confidence=0.75
    )

class ProfileRegistry:
    """Registry of preconfigured and versioned EvaluationProfiles."""
    def __init__(self):
        self._profiles: Dict[str, EvaluationProfile] = {}
        self.register(create_weapon_profile())
        self.register(create_unreal_ready_profile())
        self.register(create_visual_asset_profile())

    def register(self, profile: EvaluationProfile):
        self._profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> Optional[EvaluationProfile]:
        return self._profiles.get(profile_id)
