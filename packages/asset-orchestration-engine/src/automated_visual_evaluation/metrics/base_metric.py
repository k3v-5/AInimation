from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from ..core.evaluation_types import EvaluationCategory

class IVisualMetric(ABC):
    @property
    @abstractmethod
    def category(self) -> EvaluationCategory:
        pass

    @property
    @abstractmethod
    def metric_id(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, reference_data: Any, generated_data: Any, context: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Retorna (normalized_score, raw_metrics_dict)
        """
        pass
