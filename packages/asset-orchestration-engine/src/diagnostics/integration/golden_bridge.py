from typing import Optional
from ...golden import GoldenAPI, GoldenComparisonResult
from ...evaluation import EvaluationBenchmark

class GoldenBridge:
    """Bridges F76 Golden Asset Library to evaluate regressions after self-debugging corrections."""
    def __init__(self, golden_api: Optional[GoldenAPI] = None):
        self.golden_api = golden_api or GoldenAPI()

    def compare_with_active_golden(self, semantic_id: str, benchmark: EvaluationBenchmark) -> Optional[GoldenComparisonResult]:
        active_golden = self.golden_api.get_active_golden(semantic_id)
        if not active_golden:
            return None
        return self.golden_api.compare_with_golden(benchmark, active_golden.golden_id)
