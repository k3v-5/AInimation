from typing import Dict, List, Tuple
from ..core.evaluation_schema import EvaluationReport

class RegressionDetector:
    @staticmethod
    def check_regression(before: EvaluationReport, after: EvaluationReport) -> Tuple[bool, str]:
        # Si alguna dimensión cayó más de 0.15 puntos
        for dim, b_score in before.dimension_scores.items():
            a_score = after.dimension_scores.get(dim, b_score)
            if b_score - a_score >= 0.15:
                return True, f"REGRESSION_DETECTED: Dimension '{dim}' degraded from {b_score:.2f} to {a_score:.2f}."
        return False, "No regression detected."

class OscillationDetector:
    @staticmethod
    def check_stagnation_or_cycle(history: List[float], threshold: float = 0.02) -> Tuple[bool, str]:
        if len(history) >= 3:
            # Comprobar delta de mejora en las últimas iteraciones
            delta = abs(history[-1] - history[-2])
            if delta < threshold and abs(history[-2] - history[-3]) < threshold:
                return True, f"NO_MEANINGFUL_IMPROVEMENT: Score delta {delta:.4f} < {threshold} over consecutive iterations."

        if len(history) >= 4:
            # Comprobar ciclo A -> B -> A -> B
            if abs(history[-1] - history[-3]) < 0.01 and abs(history[-2] - history[-4]) < 0.01:
                return True, "REPAIR_OSCILLATION: Alternating state detected across repair steps."

        return False, "Progress normal."
