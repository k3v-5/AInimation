from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List

class QualityStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    UNABLE_TO_ASSESS = "UNABLE_TO_ASSESS"

@dataclass
class QualityWeights:
    silhouette_weight: float = 0.40
    dimension_weight: float = 0.40
    structural_weight: float = 0.20

class QualityGate:
    @staticmethod
    def evaluate(
        silhouette_score: float,
        dimension_score: float,
        structural_score: float,
        weights: QualityWeights = QualityWeights(),
        pass_threshold: float = 0.90,
        warning_threshold: float = 0.75
    ) -> tuple[QualityStatus, float]:
        """
        Calcula el score ponderado compuesto y determina el QualityStatus.
        """
        composite_score = round(
            (silhouette_score * weights.silhouette_weight) +
            (dimension_score * weights.dimension_weight) +
            (structural_score * weights.structural_weight),
            4
        )

        if composite_score >= pass_threshold:
            status = QualityStatus.PASS
        elif composite_score >= warning_threshold:
            status = QualityStatus.PASS_WITH_WARNINGS
        else:
            status = QualityStatus.FAIL

        return status, composite_score
