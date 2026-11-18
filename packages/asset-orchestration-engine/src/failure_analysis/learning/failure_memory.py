from typing import List, Dict, Any, Optional
from ..core.failure_models import FailureRecord

class FailureMemory:
    """Historical memory of failures and solutions for learning and pattern recognition."""

    def __init__(self):
        self._records: List[FailureRecord] = []

    def record(self, failure: FailureRecord):
        self._records.append(failure)

    def find_by_semantic_id(self, semantic_id: str) -> List[FailureRecord]:
        return [f for f in self._records if f.semantic_id == semantic_id]

    def find_by_type(self, failure_type_val: str) -> List[FailureRecord]:
        return [f for f in self._records if f.failure_type.value == failure_type_val]

    def list_all(self) -> List[FailureRecord]:
        return list(self._records)
