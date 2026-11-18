from typing import List, Dict, Any
from ..core.failure_models import FailureRecord

class FailureCorrelator:
    """Discovers relationships and causal links between multiple failure records."""

    @staticmethod
    def correlate(failures: List[FailureRecord]) -> Dict[str, List[str]]:
        correlation_map: Dict[str, List[str]] = {}
        for f in failures:
            correlated = []
            for other in failures:
                if f.failure_id != other.failure_id and f.semantic_id == other.semantic_id:
                    correlated.append(other.failure_id)
            correlation_map[f.failure_id] = correlated
        return correlation_map
