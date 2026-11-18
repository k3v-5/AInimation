from typing import List, Dict, Any
from ..core.failure_models import FailureRecord

class FailureStatistics:
    """Aggregates failure metrics across pipeline executions."""

    @staticmethod
    def compute_statistics(failures: List[FailureRecord]) -> Dict[str, Any]:
        total = len(failures)
        if total == 0:
            return {
                "total_failures": 0,
                "resolved_count": 0,
                "unresolved_count": 0,
                "escalated_count": 0,
                "auto_resolution_rate": 0.0,
                "failures_by_type": {},
                "failures_by_phase": {}
            }

        resolved = sum(1 for f in failures if f.resolution == "RESOLVED")
        escalated = sum(1 for f in failures if f.status.value == "ESCALATED")
        by_type: Dict[str, int] = {}
        by_phase: Dict[str, int] = {}

        for f in failures:
            t = f.failure_type.value
            p = getattr(f, "pipeline_phase", getattr(f, "phase", "PHASE_77"))
            by_type[t] = by_type.get(t, 0) + 1
            by_phase[p] = by_phase.get(p, 0) + 1

        return {
            "total_failures": total,
            "resolved_count": resolved,
            "unresolved_count": total - resolved,
            "escalated_count": escalated,
            "auto_resolution_rate": round(resolved / total, 4) if total > 0 else 0.0,
            "failures_by_type": by_type,
            "failures_by_phase": by_phase
        }
