from typing import Optional, List
from ...failure_analysis import FailureAnalysisAPI, FailureRecord

class FailureAnalysisBridge:
    """Interacts with F77 Failure Analysis when optimization errors occur."""

    def __init__(self, failure_api: Optional[FailureAnalysisAPI] = None):
        self.failures = failure_api or FailureAnalysisAPI()

    def get_failure_history(self, semantic_id: str) -> List[FailureRecord]:
        return self.failures.get_failure_history(semantic_id)
