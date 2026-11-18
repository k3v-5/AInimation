from typing import Optional, Dict, Any, List
from ...cost_performance import CostPerformanceAPI, CandidateStrategy, OptimizationPlan

class CostPerformanceBridge:
    """Integrates with F79 Cost/Performance Optimizer."""

    def __init__(self, cp_api: Optional[CostPerformanceAPI] = None):
        self.cp = cp_api or CostPerformanceAPI()

    def optimize_production_candidate(
        self,
        semantic_id: str,
        baseline: Dict[str, Any],
        candidates: List[CandidateStrategy]
    ) -> OptimizationPlan:
        return self.cp.optimize_asset(semantic_id, baseline, candidates)
