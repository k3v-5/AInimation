from typing import Optional, List, Dict, Any
from ...failure_analysis import FailureAnalysisAPI, FailureRecord

class FailureAnalysisBridge:
    """Integrates with F77 Failure Analysis & Self-Debugging System."""

    def __init__(self, failure_api: Optional[FailureAnalysisAPI] = None):
        self.failures = failure_api or FailureAnalysisAPI()

    def analyze_failure(self, error: Exception, context: Dict[str, Any]) -> FailureRecord:
        return self.failures.capture_exception(error, context)
