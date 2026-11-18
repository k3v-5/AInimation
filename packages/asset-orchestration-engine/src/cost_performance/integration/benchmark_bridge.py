from typing import Optional, Dict, Any
from ...evaluation import EvaluationBenchmarkAPI, EvaluationBenchmark

class BenchmarkBridge:
    """Evaluates candidate quality using F75 Evaluation Benchmark System."""

    def __init__(self, eval_api: Optional[EvaluationBenchmarkAPI] = None):
        self.eval_api = eval_api or EvaluationBenchmarkAPI()

    def evaluate_candidate(self, semantic_id: str, candidate_id: str, asset_data: Dict[str, Any]) -> EvaluationBenchmark:
        bench = self.eval_api.evaluate_asset(
            asset_semantic_id=semantic_id,
            candidate_id=candidate_id,
            asset_data=asset_data
        )
        return self.eval_api.finalize_benchmark(bench.benchmark_id)
