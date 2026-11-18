from typing import Optional, Dict, Any
from ...evaluation import EvaluationBenchmarkAPI, EvaluationBenchmark

class BenchmarkBridge:
    """Bridges Strategy Learning to F75 Evaluation Benchmark System."""

    def __init__(self, eval_api: Optional[EvaluationBenchmarkAPI] = None):
        self.eval_api = eval_api or EvaluationBenchmarkAPI()

    def evaluate_strategy_candidate(
        self,
        semantic_id: str,
        candidate_id: str,
        asset_data: Dict[str, Any],
        benchmark_id: Optional[str] = None
    ) -> EvaluationBenchmark:
        bench = self.eval_api.evaluate_asset(
            asset_semantic_id=semantic_id,
            candidate_id=candidate_id,
            asset_data=asset_data,
            benchmark_id=benchmark_id
        )
        return self.eval_api.finalize_benchmark(bench.benchmark_id)
