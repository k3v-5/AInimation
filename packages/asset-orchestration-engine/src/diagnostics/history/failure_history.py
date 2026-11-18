from typing import Dict, List, Optional
from ..core.failure_models import FailureRecord

class FailureHistory:
    """Tracks historical sequence of failures, retries, and resolutions per semantic asset."""
    def __init__(self):
        self._history: Dict[str, List[FailureRecord]] = {}

    def append(self, failure: FailureRecord):
        if failure.semantic_id not in self._history:
            self._history[failure.semantic_id] = []
        self._history[failure.semantic_id].append(failure)

    def get_history(self, semantic_id: str) -> List[FailureRecord]:
        return self._history.get(semantic_id, [])
