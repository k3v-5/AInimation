import time
from typing import Dict, Any, List, Optional
from ..core.similarity_types import ReferenceType, ReferencePriority
from ..core.similarity_schema import ReferenceProfile, AssetObservation

class ReferenceAnalyzer:
    @staticmethod
    def create_profile(
        ref_id: str,
        expected_features: Dict[str, Any],
        proportions: Optional[Dict[str, float]] = None,
        applies_to: Optional[List[str]] = None,
        priority: ReferencePriority = ReferencePriority.HIGH
    ) -> ReferenceProfile:
        return ReferenceProfile(
            reference_id=ref_id,
            source_type=ReferenceType.IMAGE,
            priority=priority,
            applies_to=applies_to or ["silhouette", "proportions", "components", "materials"],
            expected_features=expected_features,
            proportions=proportions or {"roof_to_body": 0.30},
            silhouette_aspect_ratio=1.3
        )

    @staticmethod
    def detect_conflicts(ref_a: ReferenceProfile, ref_b: ReferenceProfile):
        """Detecta contradicciones entre referencias de alta prioridad."""
        if ref_a.priority in [ReferencePriority.CRITICAL, ReferencePriority.HIGH] and \
           ref_b.priority in [ReferencePriority.CRITICAL, ReferencePriority.HIGH]:
            for k, val_a in ref_a.expected_features.items():
                if k in ref_b.expected_features:
                    val_b = ref_b.expected_features[k]
                    if val_a != val_b:
                        raise ValueError(f"REFERENCE_CONFLICT: Reference '{ref_a.reference_id}' ({k}={val_a}) contradicts '{ref_b.reference_id}' ({k}={val_b}).")

class AssetObserver:
    @staticmethod
    def observe(
        asset_id: str,
        detected_features: Dict[str, Any],
        detected_proportions: Optional[Dict[str, float]] = None,
        aspect_ratio: float = 1.3
    ) -> AssetObservation:
        return AssetObservation(
            asset_id=asset_id,
            detected_features=detected_features,
            detected_proportions=detected_proportions or {"roof_to_body": 0.30},
            silhouette_aspect_ratio=aspect_ratio,
            bounds={"w": 6.0, "d": 4.0, "h": 4.5}
        )
