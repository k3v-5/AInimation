from typing import List, Dict, Any
from .corrective_action import CorrectiveAction

class CorrectionHistory:
    """Tracks applied corrective actions and records their outcomes."""

    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def record_correction(self, action: CorrectiveAction, outcome: str, details: Dict[str, Any]):
        self._history.append({
            "action": action.to_dict(),
            "outcome": outcome,
            "details": details
        })

    def list_corrections(self) -> List[Dict[str, Any]]:
        return list(self._history)
