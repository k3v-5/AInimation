from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class QualityWeights:
    silhouette: float = 0.25
    proportion: float = 0.20
    components: float = 0.20
    material: float = 0.10
    color: float = 0.05
    style: float = 0.10
    geometry: float = 0.10

@dataclass
class VerificationReport:
    asset_id: str
    overall_score: float
    status: str # PASS, PASS_WITH_WARNINGS, NEEDS_CORRECTION, FAIL
    hard_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommended_action: str = "NONE" # NONE, LOCAL_MODIFICATION, PARAMETRIC_SCALE, REGENERATE

class QualityScorer:
    @staticmethod
    def calculate_score(
        asset_id: str,
        metrics: Dict[str, float],
        hard_failures: List[str],
        warnings: List[str],
        evidence: Dict[str, Any],
        weights: Optional[QualityWeights] = None
    ) -> VerificationReport:
        w = weights or QualityWeights()

        overall = round(
            metrics.get("silhouette", 1.0) * w.silhouette +
            metrics.get("proportion", 1.0) * w.proportion +
            metrics.get("components", 1.0) * w.components +
            metrics.get("material", 1.0) * w.material +
            metrics.get("color", 1.0) * w.color +
            metrics.get("style", 1.0) * w.style +
            metrics.get("geometry", 1.0) * w.geometry,
            4
        )

        # Regla Inflexible: Hard Constraint Failure => FAIL inmediato
        if len(hard_failures) > 0:
            status = "FAIL"
            rec_action = "LOCAL_MODIFICATION" if overall >= 0.60 else "REGENERATE"
        elif overall >= 0.90:
            status = "PASS"
            rec_action = "NONE"
        elif overall >= 0.80:
            status = "PASS_WITH_WARNINGS"
            rec_action = "NONE"
        elif overall >= 0.65:
            status = "NEEDS_CORRECTION"
            rec_action = "LOCAL_MODIFICATION"
        else:
            status = "FAIL"
            rec_action = "REGENERATE"

        return VerificationReport(
            asset_id=asset_id,
            overall_score=overall,
            status=status,
            hard_failures=hard_failures,
            warnings=warnings,
            evidence=evidence,
            recommended_action=rec_action
        )
