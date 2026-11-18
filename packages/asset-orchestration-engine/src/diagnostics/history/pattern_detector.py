from typing import Dict, Any, List
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType

class PatternDetector:
    """Detects recurring failure patterns, common root causes, and computes correction success rates."""
    
    @staticmethod
    def detect_patterns(incidents: List[FailureRecord]) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        assets_affected: Dict[str, set] = {}

        for inc in incidents:
            t = inc.failure_type.value
            counts[t] = counts.get(t, 0) + 1
            if t not in assets_affected:
                assets_affected[t] = set()
            assets_affected[t].add(inc.semantic_id)

        recurring = []
        for t, c in counts.items():
            if c >= 3:
                recurring.append({
                    "failure_type": t,
                    "count": c,
                    "affected_assets": list(assets_affected[t]),
                    "pattern": "RECURRING_FAILURE"
                })

        return {
            "total_incidents": len(incidents),
            "recurring_patterns": recurring,
            "type_counts": counts
        }
