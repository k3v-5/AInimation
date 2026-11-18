import math
from typing import Dict, Any, List, Tuple
from ..core.critic_schema import (
    ReferenceImageSpec, SilhouetteMetrics, ProportionMetrics, MaterialMetrics
)

class SilhouetteAnalyzer:
    @staticmethod
    def analyze(ref: ReferenceImageSpec, generated_aspect_ratio: float) -> SilhouetteMetrics:
        # Calcular error de relación de aspecto
        ar_diff = abs(ref.expected_aspect_ratio - generated_aspect_ratio)
        ar_err = round(generated_aspect_ratio - ref.expected_aspect_ratio, 3)

        # IoU estimado a partir de la discrepancia de proporción de silueta
        iou = max(0.0, min(1.0, 1.0 - (ar_diff / ref.expected_aspect_ratio)))
        hausdorff = round(ar_diff * 0.25, 3)
        score = round(iou * 0.8 + (1.0 - min(1.0, hausdorff)) * 0.2, 3)

        return SilhouetteMetrics(
            iou=round(iou, 3),
            hausdorff_distance=hausdorff,
            aspect_ratio_error=ar_err,
            score=score
        )

class ProportionAnalyzer:
    @staticmethod
    def analyze(
        ref: ReferenceImageSpec,
        gen_roof_ratio: float,
        user_window_count: int,
        gen_window_count: int
    ) -> ProportionMetrics:
        roof_diff = abs(ref.expected_roof_ratio - gen_roof_ratio)
        roof_err = round(gen_roof_ratio - ref.expected_roof_ratio, 3)

        prop_score = max(0.0, 1.0 - roof_diff * 2.0)

        # Si el usuario pidió explícitamente 4 ventanas y el asset tiene 4, no penalizar
        if gen_window_count != user_window_count:
            prop_score -= 0.20

        return ProportionMetrics(
            roof_to_body_error=roof_err,
            width_to_height_error=0.0,
            score=round(max(0.0, prop_score), 3)
        )

class MaterialAnalyzer:
    @staticmethod
    def analyze_lab_color(ref_lab: List[float], gen_lab: List[float]) -> MaterialMetrics:
        # Delta E estándar: sqrt((L1-L2)^2 + (a1-a2)^2 + (b1-b2)^2)
        delta_e = math.sqrt(
            (ref_lab[0] - gen_lab[0]) ** 2 +
            (ref_lab[1] - gen_lab[1]) ** 2 +
            (ref_lab[2] - gen_lab[2]) ** 2
        )
        delta_e = round(delta_e, 2)
        # Delta E < 2.0 es imperceptible para el ojo humano
        score = max(0.0, min(1.0, 1.0 - (delta_e / 50.0)))
        return MaterialMetrics(delta_e=delta_e, score=round(score, 3))
