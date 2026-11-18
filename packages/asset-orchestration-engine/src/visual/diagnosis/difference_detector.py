from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class DifferenceType(str, Enum):
    LENGTH = "LENGTH"
    WIDTH = "WIDTH"
    HEIGHT = "HEIGHT"
    DEPTH = "DEPTH"
    MISSING_COMPONENT = "MISSING_COMPONENT"
    EXTRA_COMPONENT = "EXTRA_COMPONENT"
    PROPORTION = "PROPORTION"
    SILHOUETTE = "SILHOUETTE"
    SCALE = "SCALE"
    UNOBSERVED = "UNOBSERVED"

@dataclass
class DifferenceRecord:
    target_component: str
    diff_type: DifferenceType
    severity: float # 0.0 -> negligible, 1.0 -> critical
    confidence: float # 0.0 -> 1.0
    current_value: Any = None
    expected_value: Any = None
    axis: Optional[str] = None
    message: str = ""

class DifferenceDetector:
    @staticmethod
    def detect_differences(
        dimension_deltas: List[Dict[str, Any]],
        structural_features: Dict[str, Any],
        silhouette_score: float,
        silhouette_threshold: float = 0.85
    ) -> List[DifferenceRecord]:
        differences: List[DifferenceRecord] = []

        # 1. Componentes Ausentes
        for mc in structural_features.get("missing_components", []):
            differences.append(DifferenceRecord(
                target_component=mc,
                diff_type=DifferenceType.MISSING_COMPONENT,
                severity=1.0,
                confidence=1.0,
                message=f"Required component '{mc}' is missing from asset."
            ))

        # 2. Componentes Extra
        for ec in structural_features.get("extra_components", []):
            differences.append(DifferenceRecord(
                target_component=ec,
                diff_type=DifferenceType.EXTRA_COMPONENT,
                severity=0.60,
                confidence=0.95,
                message=f"Unauthorized extra component '{ec}' detected."
            ))

        # 3. Desviaciones Dimensionales
        for delta in dimension_deltas:
            cid = delta["component_id"]
            axis = delta["axis"]
            rel_err = delta["relative_error"]
            
            dtype = DifferenceType.LENGTH if axis == "height" else (DifferenceType.WIDTH if axis == "width" else DifferenceType.DEPTH)
            sev = min(1.0, round(rel_err * 2.0, 2)) # e.g. 10% error -> 0.20 severity

            differences.append(DifferenceRecord(
                target_component=cid,
                diff_type=dtype,
                severity=sev,
                confidence=0.95,
                current_value=delta["current"],
                expected_value=delta["expected"],
                axis=axis,
                message=f"Component '{cid}' {axis} deviates: actual {delta['current']}m vs expected {delta['expected']}m (delta={delta['delta']}m)."
            ))

        # 4. Desviación Global de Silueta (si no hubo deltas dimensionales explícitos pero la silueta difiere)
        if silhouette_score < silhouette_threshold and not dimension_deltas:
            differences.append(DifferenceRecord(
                target_component="asset",
                diff_type=DifferenceType.SILHOUETTE,
                severity=round(1.0 - silhouette_score, 2),
                confidence=0.85,
                current_value=silhouette_score,
                expected_value=1.0,
                message=f"Silhouette match is low ({round(silhouette_score * 100, 1)}% < {round(silhouette_threshold * 100, 1)}%)."
            ))

        return differences
