from typing import Dict, List, Any, Optional
from ..core.evaluation_types import EvaluationCategory
from ..core.evaluation_schema import CategoryEvaluation, EvaluationConfiguration
from .base_metric import IVisualMetric
from .silhouette_metric import SilhouetteMetric
from .proportion_metric import ProportionMetric
from .color_material_metric import ColorMaterialMetric
from .lighting_metric import LightingMetric

class MetricRegistry:
    def __init__(self):
        self._metrics: Dict[str, IVisualMetric] = {}
        self._register_default_metrics()

    def _register_default_metrics(self):
        self.register(SilhouetteMetric())
        self.register(ProportionMetric())
        self.register(ColorMaterialMetric())
        self.register(LightingMetric())

    def register(self, metric: IVisualMetric):
        self._metrics[metric.metric_id] = metric

    def get(self, metric_id: str) -> Optional[IVisualMetric]:
        return self._metrics.get(metric_id)

    def evaluate_all(
        self,
        reference_data: Any,
        generated_data: Any,
        context: Dict[str, Any],
        config: EvaluationConfiguration
    ) -> Dict[str, CategoryEvaluation]:
        cat_evals: Dict[str, CategoryEvaluation] = {}
        
        for metric in self._metrics.values():
            cat = metric.category
            if cat not in config.enabled_categories:
                continue

            score, raw_metrics = metric.evaluate(reference_data, generated_data, context)
            weight = config.weights.get(cat.value, 1.0)

            if cat.value not in cat_evals:
                cat_evals[cat.value] = CategoryEvaluation(
                    category=cat,
                    score=score,
                    weight=weight,
                    confidence=0.95,
                    status="EVALUATED",
                    metrics=raw_metrics
                )
            else:
                existing = cat_evals[cat.value]
                existing.score = round((existing.score + score) / 2.0, 4)
                existing.metrics.update(raw_metrics)

        return cat_evals
