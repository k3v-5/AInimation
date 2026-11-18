from typing import Optional, List, Dict, Any
from ...failure_analysis import FailureAnalysisAPI, FailureRecord

class FailureAnalysisBridge:
    """Bridges Strategy Learning to F77 Failure Analysis & Self-Debugging System."""

    def __init__(self, failure_api: Optional[FailureAnalysisAPI] = None):
        self.failures = failure_api or FailureAnalysisAPI()

    def get_failures_for_strategy(self, semantic_id: str) -> List[FailureRecord]:
        return self.failures.get_failure_history(semantic_id)
