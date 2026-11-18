from typing import List, Optional, Dict, Any
from ..core.failure_models import FailureRecord

class SolutionReuseEngine:
    """Recommends historical proven solutions for matching failure signatures."""

    @staticmethod
    def recommend_solution(failure_type_val: str, history: List[FailureRecord]) -> Optional[str]:
        matching = [
            f for f in history
            if f.failure_type.value == failure_type_val and f.resolution == "RESOLVED"
        ]
        if matching:
            # Return the most frequent successful action
            actions: Dict[str, int] = {}
            for m in matching:
                act = m.recommended_action
                actions[act] = actions.get(act, 0) + 1
            return max(actions.items(), key=lambda x: x[1])[0]
        return None
