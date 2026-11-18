from typing import Dict, Any, Optional
from ..core.reference_schema import ReferenceProfile, ErrorMap, ProportionFeature
from ..matching.geometric_matcher import GeometricMatcher

class VisualReferenceAPI:
    """
    Visual Reference Understanding & Geometric Matching API (AOE v25)
    
    Regla Fundamental:
    TRANSFORMA REFERENCIAS VISUALES EN PERFILES GEOMÉTRICOS COMPARABLES.
    GENERA ERROR MAP CON DISCREPANCIAS Y PARCHES RECOMENDADOS (DELTA PERCENT).
    """
    def __init__(self):
        pass

    def create_reference_profile(
        self,
        reference_id: str,
        source_uri: str,
        proportions: Dict[str, float],
        detected_components: list = None,
        style_attributes: Dict[str, str] = None
    ) -> ReferenceProfile:
        prop_objs = {
            k: ProportionFeature(k, v) for k, v in proportions.items()
        }
        return ReferenceProfile(
            reference_id=reference_id,
            source_uri=source_uri,
            proportions=prop_objs,
            detected_components=detected_components or ["foundation", "walls", "roof", "windows"],
            style_attributes=style_attributes or {"style": "medieval_stylized"}
        )

    def compare_model(
        self,
        target_asset_id: str,
        model_data: Dict[str, Any],
        reference: ReferenceProfile
    ) -> ErrorMap:
        return GeometricMatcher.compare_model_against_reference(
            target_asset_id=target_asset_id,
            model_data=model_data,
            reference=reference
        )
