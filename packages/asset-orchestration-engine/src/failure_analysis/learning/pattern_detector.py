from typing import List, Dict, Any
from ..core.failure_models import FailureRecord

class PatternDetector:
    """Detects recurring failure patterns and frequent root causes."""

    @staticmethod
    def detect_patterns(failures: List[FailureRecord]) -> Dict[str, Any]:
        type_counts: Dict[str, int] = {}
        asset_counts: Dict[str, int] = {}

        for f in failures:
            t = f.failure_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
            asset_counts[f.semantic_id] = asset_counts.get(f.semantic_id, 0) + 1

        recurring_types = [k for k, v in type_counts.items() if v >= 2]
        recurring_assets = [k for k, v in asset_counts.items() if v >= 2]

        return {
            "total_incidents": len(failures),
            "type_counts": type_counts,
            "asset_counts": asset_counts,
            "recurring_types": recurring_types,
            "recurring_assets": recurring_assets,
            "has_recurring_issues": len(recurring_types) > 0
        }
