from typing import Dict, Any, Optional
from ..core.loop_schema import IterationRecord

class BestStateTracker:
    def __init__(self):
        self.best_iteration_number: int = 0
        self.best_quality_score: float = -1.0
        self.best_state_hash: str = ""
        self.best_state_payload: Dict[str, Any] = {}

    def update_best(
        self,
        iter_num: int,
        score: float,
        state_hash: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> bool:
        if score > self.best_quality_score:
            self.best_iteration_number = iter_num
            self.best_quality_score = round(score, 4)
            self.best_state_hash = state_hash
            self.best_state_payload = payload or {}
            return True
        return False
