from typing import List, Dict
from ..core.scoring_types import MetricCategory, MetricStatus
from ..core.scoring_schema import QualityMetric, QualityProfile

class QualityScorer:
    @classmethod
    def calculate_scores(
        cls,
        metrics: List[QualityMetric],
        profile: QualityProfile
    ) -> Dict[str, float]:
        # Agrupar métricas por categoría
        cat_values: Dict[MetricCategory, List[float]] = {}
        for m in metrics:
            if m.status == MetricStatus.VALID:
                cat_values.setdefault(m.category, []).append(m.normalized_value)

        category_scores: Dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for cat, weight in profile.weights.items():
            if cat in cat_values and len(cat_values[cat]) > 0:
                avg_val = sum(cat_values[cat]) / len(cat_values[cat])
                category_scores[cat.value] = round(avg_val * 100.0, 2)
                weighted_sum += avg_val * weight
                total_weight += weight
            else:
                category_scores[cat.value] = 100.0 # Default if category has no evaluated defects
                weighted_sum += 1.0 * weight
                total_weight += weight

        overall_score = (weighted_sum / total_weight) * 100.0 if total_weight > 0 else 100.0
        category_scores["OVERALL"] = round(overall_score, 2)

        return category_scores
